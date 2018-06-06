#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os
import shutil
import platform
import re

__dir__ = os.path.dirname(os.path.abspath(__file__))

def _UNUSED(*param):
    pass



class NodePlugin(ConanFile):
    name = "plugin.node"
    version = "0.5.2-dev"
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

    def build(self):
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

        filename = os.path.join('addon/src/version.h')
        f = open( filename,'wb')
        f.write('''#define __VERSION__ "%s"
        '''%self.version)
        f.close()

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

        