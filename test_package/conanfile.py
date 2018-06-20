#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools, RunEnvironment
import os
import platform


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    if platform.system() == "Windows":
        prefix=''
    else:
        prefix='lib'

    def imports(self):
        for p in  self.deps_cpp_info.bin_paths:
            filename = os.path.join( p,'plugin.node')
            print(filename,'<=============================',os.path.exists( filename ))
            
            if os.path.exists( filename ):
                self.copy('plugin.node',dst='bin',src=p)
                self.copy('%scase-converter-plugin%s'%(self.prefix,self._EXT()),dst='bin',src=p)

    #def build(self):
    #    cmake = CMake(self)
    #    cmake.configure()
    #    cmake.build()

    def test(self):
        self.run("sudo pip install cpplint")
        for (root, dirs, files) in os.walk("%s/../addon/src" % os.path.dirname(__file__)):
            for filename in files:
                print os.path.join(root,filename)
                self.run("cpplint --filter=-whitespace/tab,-whitespace/braces,-build/header_guard,-readability/casting,-build/include_order,-build/include --linelength=120 %s" % os.path.join(root,filename))
        
        with tools.environment_append(RunEnvironment(self).vars):
            command ='node test.js {0}/bin/plugin.node {0}/bin/{1}case-converter-plugin{2}'.format(
                os.path.abspath('.'), self.prefix, self._EXT())
            if self.settings.os == "Linux":
                command = 'LD_LIBRARY_PATH=%s ' % (os.path.abspath('.')+'/bin') + command
            self.run(command,cwd = os.path.dirname(__file__))


    def _EXT(self):
        if self.settings.os == "Windows":
            return '.dll'
        elif self.settings.os == "Macos":
            return '.dylib'
        else: # Linux
            return '.so'

