#!/usr/bin/env python
# -*- coding: utf-8 -*-
import platform
import os
from bincrafters import build_template_default

import copy


if __name__ == "__main__":

    #
    #  seems the Visual Studio 2017 could not find in windows
    #
    if platform.system() == "Windows" and os.environ.get('CONAN_VISUAL_VERSIONS',None) is None:
        os.environ['CONAN_VISUAL_VERSIONS'] ="15"

    directory = os.path.abspath(os.path.dirname(__file__))
    
    os.environ['NODE_PLUGIN_SOURCE_FOLDER'] = directory

    builder = build_template_default.get_builder()

    items = []
    for item in builder.items:
        if item.settings["arch"] != "x86_64":
            continue
        if len(items) >0 :
            break
        # skip static
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
