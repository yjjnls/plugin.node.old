#!/usr/bin/env python
# -*- coding: utf-8 -*-
import platform
import os
import sys
from bincrafters import build_template_default

import copy

def build():
    builder = build_template_default.get_builder()

    items = []
    for item in builder.items:
        print("#####",item.settings)
        if not item.options["plugin.node:shared"]:
           print("NOT SHARED")
           continue

        # Visual Sutido 2017 only
        if not (platform.system() == "Windows" and item.settings["compiler"] == "Visual Studio" and
                item.settings["compiler.version"] == '15' ):
            print("NOT VS")
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
        
    os.environ['CONAN_VISUAL_VERSIONS'] = '15'
    os.environ['CONAN_BUILD_TYPES']='Release'
    archs = ['x86_64','x86']
    for arch in archs:
        os.environ['CONAN_ARCHS']=arch
        sys.path.insert(0, os.path.dirname(__file__)+'/devutils')        
        
        nvm = devutils.software.NodeVersioManager()
        nvm.use( arch, '^8.11')
        build()

if __name__ == "__main__":

    import sys
    if len(sys.argv) >1 and sys.argv[1]=='nvm':
        build_with_nvm()
    else:
        build()

