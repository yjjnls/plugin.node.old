#!/usr/bin/env python
# -*- coding: utf-8 -*-
import platform
import os
import sys
import copy
import re
import subprocess
import shlex
import platform
import semver

from bincrafters import build_template_default

def load_version():
    filename = os.path.join(os.path.dirname(__file__), 'addon/src/version.h')

    with open(filename, "rt") as version_file:
        content = version_file.read()
        version = re.search(r'#define __VERSION__\s+"([0-9a-z.-]+)"', content).group(1)
        return version

def load_conanfile_version():
    filename = os.path.join(os.path.dirname(__file__), 'conanfile.py')

    with open(filename, "rt") as version_file:
        content = version_file.read()
        version = re.search(r'''version\s*=\s*["'](\S*)["']''', content).group(1)
        return version

def bump_version(release='patch'):
    version = ver or load_version()
    Ver = semver.SemVer( ver or load_conanfile_version())
    #bumps old ver to new version
    version = Ver.inc( release )

    filename = os.path.join(os.path.dirname(__file__), 'addon/src/version.h')
    f = open(filename,'w');
    f.write( '#define __VERSION__ "%s"'%version)
    f.close()

    




    with open(filename, "w") as version_file:
        content = version_file.read()
        version = re.search(r'#define __VERSION__\s+"([0-9a-z.-]+)"', content).group(1)
        return version

def build():
    builder = build_template_default.get_builder()

    items = []
    for item in builder.items:
        if not item.options["plugin.node:shared"]:
           continue

        # Visual Sutido 2017 only
        if not (platform.system() == "Windows" and item.settings["compiler"] == "Visual Studio" and
                item.settings["compiler.version"] == '15' ):
            continue
    
        # skip mingw cross-builds
        if not (platform.system() == "Windows" and item.settings["compiler"] == "gcc" and
                item.settings["arch"] == "x86"):
            items.append(item)
        

    builder.items = items

    builder.run()


def build_with_nvm():
    try:
        import devutils
        import devutils.software        
    except:
        raise Exception('Please install devutils < pip install devutils >.')
        
    
    os.environ['CONAN_BUILD_TYPES']='Release'
    archs = ['x86_64','x86']
    for arch in archs:
        os.environ['CONAN_ARCHS']=arch
        sys.path.insert(0, os.path.dirname(__file__)+'/devutils')        
        
        nvm = devutils.software.NodeVersioManager()
        nvm.use( arch, '^8.11')
        build()
        return

if __name__ == "__main__":
    if os.environ.get('CONAN_STABLE_BRANCH_PATTERN',None) is None:
        os.environ['CONAN_STABLE_BRANCH_PATTERN'] = 'master'
    if platform.system() == 'Windows' and os.environ.get('CONAN_VISUAL_VERSIONS',None) is None:
        os.environ['CONAN_VISUAL_VERSIONS'] = '15'


    if len(sys.argv) >1 and sys.argv[1]=='nvm':
        build_with_nvm()
    else:
        build()

