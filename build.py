#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
import sys
import os
import re
import platform
from shell import shell as call
from cpt.packager import ConanMultiPackager
from conans.client.loader_parse import load_conanfile_class
__dir__ =os.path.dirname(os.path.abspath(__file__))

PACKAGE_NAME   = 'plugin.node'
CONAN_USERNAME = 'pluginx'

def get_build_number():
    '''
    Get current git repo commits time since last tag.
    if no commit, this is an tag
    '''
    commitid = call('git rev-list --tags --no-walk --max-count=1')
    count    = call('git rev-list  %s.. --count'%commitid.output()[0])

    return int(count.output()[0])

def update_version(version):
    # conanfile.py
    f = open( os.path.join(__dir__, 'conanfile.py'), 'rt')
    content = f.read()
    f.close()#
    P_VERSION = re.compile(r'''version\s*=\s*["'](?P<version>\S*)["']''')
    def _replace(m):
        return 'version = "%s"'%version
    content = P_VERSION.sub(_replace, content)
    f = open(os.path.join(__dir__, 'conanfile.py'),'wb')
    f.write( content )
    f.close()

    # addon 
    f = open(os.path.join(__dir__,'addon/src/version.h') ,'wb')
    f.write(r'#define __VERSION__ "%s\n"'%version)
    f.close()
    return ['conanfile.py','addon/src/version.h']


def build():
    n             = get_build_number()
    conanfile = load_conanfile_class(os.path.join(__dir__,'conanfile.py'))
    version = conanfile.version


    if n == 0:
        CONAN_CHANNEL = 'stable'
        CONAN_UPLOAD_ONLY_WHEN_STABLE = True        
    else:
        version = '%s.%d'%(version,n)
        CONAN_CHANNEL = 'testing'
        CONAN_UPLOAD_ONLY_WHEN_STABLE = False
        update_version(version)


    CONAN_UPLOAD  = 'https://api.bintray.com/conan/%s/%s'%(CONAN_USERNAME,CONAN_CHANNEL)

    builder = ConanMultiPackager(
        channel=CONAN_CHANNEL,
        upload_only_when_stable= CONAN_UPLOAD_ONLY_WHEN_STABLE,
        upload=CONAN_UPLOAD,     
        username=CONAN_USERNAME
    )

    builder.add_common_builds()
    builds = []
    for settings, options, env_vars, build_requires, reference in builder.items:

        # dynamic only
        if not options["plugin.node:shared"]:
            continue
        # release only    
        if settings["build_type"] != "Debug":
            continue

        # Visual Sutido 2017 only
        if platform.system() == "Windows":
            if settings["compiler"] == "Visual Studio":
                if settings["compiler.version"] == '15' :
                    builds.append([settings, options, env_vars, build_requires])
        else:
            builds.append([settings, options, env_vars, build_requires])


    builder.run()


if __name__ == '__main__':
    '''
    windows release x86
    set CONAN_VISUAL_VERSIONS=5
    set CONAN_BUILD_TYPES=Release
    set CONAN_ARCHS=x86
    python build.py

    '''

    build()
