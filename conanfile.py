#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os
import shutil
import platform
import re
__directory__ = os.environ.get('NODE_PLUGIN_SOURCE_FOLDER' ,
                os.path.abspath(os.path.dirname(__file__)))

def _UNUSED(*param):
    pass

def check_call(cmd, cmd_dir=None):
    import sys
    import shlex
    import subprocess

    if isinstance(cmd, str):
        cmd = shlex.split(cmd)
    process = subprocess.Popen(cmd, cwd=cmd_dir,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, shell=True)
    output, err = process.communicate()
    if process.poll():
        raise Exception("runing command %s failed"%cmd)

    if sys.stdout.encoding:
        output = output.decode(sys.stdout.encoding)

    if sys.stdout.encoding:
        err = err.decode(sys.stdout.encoding)

    return output,err
def is_same_dir(a,b):
    def normpath( p ):
        return os.path.normpath( 
            os.path.abspath(p) ).replace('\\','/')
    print("*",normpath(a) == normpath(b),normpath(a) , normpath(b))
    return normpath(a) == normpath(b)


class NodePlugin(ConanFile):
    name = "plugin.node"
    version = "0.4.3"
    url = "https://github.com/Mingyiz/plugin.node"
    homepage = url
    description = "Node.js addon for c plugin dynamic."
    license = "Apache-2.0"

#    exports = ["LICENSE"]
    exports_sources = "addon/*",'plugin/*'
    generators = "cmake"

    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True,False],
               "fPIC": [True, False]
              }
    default_options = ("shared=True",
                       "fPIC=True")

    source_subfolder = "source_subfolder"

    def requirements(self):
        pass

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.remove("fPIC")
        self.options["node-plugin"].shared=True
    def _version_check(self):
        return
        filename = os.path.join( 'addon/src/version.h')
        with open(filename, "rt") as version_file:
            content = version_file.read()
            version = re.search(r'#define __VERSION__\s+"([0-9a-z.-]+)"', content).group(1)
            if version != self.version:
                raise Exception('conanfile.py version %s diff with %s in addon/src/version.h'%(self.version,version))
        

    def build(self):
        self._version_check()


        options = {
            'arch':'x64',
            'compiler': '',
            'debug':'',
            'python': '',
        }
        if os.environ.get('PYTHON',None):
            options['python'] = '--python %s'%os.environ['PYTHON']


        if self.settings.build_type =="Debug":
            options["debug"]="--debug"

        if platform.system() == "Windows":
            if self.settings.arch == "x86":
                options["arch"] = "ia32"

            if self.settings.compiler == "Visual Studio":
                _COMPILER={'15':'--msvs_version=2017',
                '14':'--msvs_version=2015' }
                msvs = str(self.settings.compiler.version)
                assert ( msvs in _COMPILER.keys())
                options["compiler"] = _COMPILER[msvs]

        self.run("node-gyp -C addon %(python)s configure %(compiler)s --arch=%(arch)s "%options)
        self.run("node-gyp -C addon %(python)s build %(debug)s "%options)

        cmake = CMake(self)
        cmake.configure(source_folder='plugin')
        cmake.build()
        #cmake.install()

    def package(self):
        ext='.dll'
        if self.settings.os == 'Linux':
            ext = '.so'

        src = 'addon/build/%s'%self.settings.build_type

        self.copy(pattern= 'plugin.node', dst="bin",src = src)
        self.copy(pattern= 'bin/case-converter-plugin%s'%ext)

        
    def _enviroment_check(self):
        
        check_call('node-gyp --version')
        self._python_check()

    def _python_check(self):
        from conans.client.tools.files import which
        self.PYTHON = os.environ.get('PYTHON2',
                      os.environ.get('PYTHON',None))
        if self.PYTHON is None:
            self._python = which('python')
            if self._python is None:
                raise Exception("python program not exists.")
        
        python3, version = check_call('python --version', self.PYTHON)
        if not version:
            raise Exception(" only python2 support. detected <%s>"%python3.strip())
        
        version = version.split()[1]
        if version  > '3.0.0':
            raise Exception(" only python2 support.")
        

        