#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools, RunEnvironment
import os
import platform

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        #builddirs_plugin.node
        #bindir = self.deps_env_info["bindirs_plugin.node"]
        #print(self.deps_env_info,"<~~~~~~~~~",self.deps_cpp_info.bin_paths)
        #print(self.build_folder)
        PLUGIN_NODE_PATH = None
        for p in  self.deps_cpp_info.bin_paths:
            filename = os.path.join( p,'plugin.node')
            if os.path.exists( filename ):
                PLUGIN_NODE_PATH = filename
        
        TEST_CONVERTER_PATH = os.path.join(self.build_folder,'bin','converter.so')
        if platform.system() == 'Windows':
            TEST_CONVERTER_PATH = os.path.join(self.build_folder,'bin','converter.dll')
        #print("%s\n%s\n%s\n%s\n"%(PLUGIN_NODE_PATH,TEST_CONVERTER_PATH,os.path.abspath('.'),os.path.dirname(__file__)))
        assert( os.path.exists( PLUGIN_NODE_PATH) and os.path.exists( TEST_CONVERTER_PATH) )


        
        with tools.environment_append(RunEnvironment(self).vars):
            print(os.path.abspath('.'))
            self.run('node test.js %s %s'%(PLUGIN_NODE_PATH,TEST_CONVERTER_PATH),cwd = os.path.dirname(__file__))
            #os.environ['PLUGIN_NODE_DIRECTORY'] = PLUGIN_NODE_DIRECTORY
            #bin_path = os.path.join("bin", "test_package")
            #if self.settings.os == "Windows":
            #    self.run(bin_path)
            #elif self.settings.os == "Macos":
            #    self.run("DYLD_LIBRARY_PATH=%s %s" % (os.environ.get('DYLD_LIBRARY_PATH', ''), bin_path))
            #else:
            #    self.run("LD_LIBRARY_PATH=%s %s" % (os.environ.get('LD_LIBRARY_PATH', ''), bin_path))
