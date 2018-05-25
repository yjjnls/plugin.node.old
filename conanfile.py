#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os
import shutil
import platform

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
    version = "0.3.0"
    url = "https://github.com/Mingyiz/plugin.node"
    homepage = url
    description = "Node.js addon for c plugin dynamic."
    license = "Apache-2.0"

    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]
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
        

    def build(self):
        print("**************** package *******************************")
        print(os.path.abspath("."))
        print("***********************************************")

        self._enviroment_check()
        self._build_addon()

        #cmake = CMake(self)
        #cmake.configure(source_folder=__directory__)
        #cmake.build()

        # Explicit way:
        # self.run('cmake "%s/src" %s' % (self.source_folder, cmake.command_line))
        # self.run("cmake --build . %s" % cmake.build_config)

    def package(self):
        #self.copy(pattern="leptonica-license.txt", dst="licenses", src=self.source_subfolder)
        #print("$$$$$",os.path.abspath('.'))
        #print("**************** package *******************************")
        #print(os.path.abspath("."))
        #print(self.copy)
        #print(self.copy._base_dst)
        #print(self.copy._base_src)
        #print("***********************************************")
        

        src = 'addon/build/%s'%self.settings.build_type

        self.copy(pattern= 'plugin.node', dst="bin",src = src)
        #self.copy(pattern="*.lib", dst="lib", keep_path=False)

    #def package_info(self):
    #    self.cpp_info.libs = tools.collect_libs(self)

    def _build_addon(self):
        #CD = os.getcwd()
        #print(CD,"<------",__directory__)
        #print(self.build_folder)

        # if out build, copy src to there
        #print(self.build_folder, __directory__)
        if not is_same_dir( self.build_folder, __directory__):
            shutil.copytree( os.path.join(__directory__,"addon"),
            os.path.join(self.build_folder,"addon"))

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
        #os.chdir(CD)

        
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
        

        