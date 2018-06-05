#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
import sys
import os
import re
import semver
import devutils
import argparse
from devutils.shell import check_call,prompt,call
from devutils import git
import platform
from bincrafters import build_template_default
def build():
    print("===>",os.environ.get('CONAN_UPLOAD_ONLY_WHEN_STABLE'))
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


class ReleaseManager(object):

    _version = None
    _conanfile_version = None


    def __init__(self):
        self._version = self._load_version()
        self._conanfile_version = self._load_conanfile_version()

    def _load_version(self):
        filename = os.path.join(os.path.dirname(__file__), 'addon/src/version.h')

        with open(filename, "rt") as version_file:
            content = version_file.read()
            version = re.search(r'#define __VERSION__\s+"([0-9a-z.-]+)"', content).group(1)
            return version
        raise Exception('can not version.')

    def _load_conanfile_version(self):
        filename = os.path.join(os.path.dirname(__file__), 'conanfile.py')

        with open(filename, "rt") as version_file:
            content = version_file.read()
            version = re.search(r'''version\s*=\s*["'](\S*)["']''', content).group(1)
            return version
        raise Exception('can not file version in conanfile.py')

    def _update_version( self, version , conan_only = False):
        
        filename = os.path.join(os.path.dirname(__file__), 'conanfile.py')

        f = open(filename, 'rt')
        content = f.read()
        f.close()

        P_VERSION = re.compile(r'''version\s*=\s*["'](?P<version>\S*)["']''')
        def _replace(m):
            #d = m.groupdict()
            return 'version = "%s"'%version
        content = P_VERSION.sub(_replace, content)
        f = open(filename,'wb')
        content = content.replace('\r\n','\n' )
        f.write( content )
        f.close()
        if conan_only:
            return


        filename = os.path.join(os.path.dirname(__file__), 'addon/src/version.h')
        f = open(filename, 'wb')
        f.write(r'#define __VERSION__ "%s"'%version + '\n')
        f.close()



        from devutils import shell
        shell.replace('docs/release-notes.md',{'${__version__}':version})





    def _build(self,args):
        git_dir = os.path.dirname( os.path.abspath(__file__))
        n = git.get_commit_count_since_last_tag(git_dir)
        if n >0:
            
            #self._update_version(self._conanfile_version + '.%d'%n,conan_only=True)
            os.environ['CONAN_CHANNEL'] ='testing'
            os.environ['CONAN_UPLOAD']='https://api.bintray.com/conan/pluginx/testing'
            #os.environ['CONAN_UPLOAD_ONLY_WHEN_STABLE']='False'
        else:
            os.environ['CONAN_CHANNEL'] ='stable'
            os.environ['CONAN_UPLOAD']='https://api.bintray.com/conan/pluginx/stable'
            #os.environ['CONAN_UPLOAD_ONLY_WHEN_STABLE']='True'
            os.environ['CONAN_STABLE_BRANCH_PATTERN']='dev'
            
        if platform.system() == 'Windows' and os.environ.get('CONAN_VISUAL_VERSIONS',None) is None:
            os.environ['CONAN_VISUAL_VERSIONS'] = '15'

        build() #global build
    
        


    def _bump_version(self,args):
        if self._has_uncommit():
            print('you have some files not commited. please commit all of them, before bump the version.')
            os.system('git status ')
            return

        oldver = self._conanfile_version
        ver    = semver.inc( oldver, args.release,loose = True)
        
        res = prompt('''

        *********************************************************
        bump the version %s => %s
        src/addon/src/version.h
        conanfile.py
        docs/release-notes.md
        version related infomation will update to the new version.
        '''%(oldver,ver), ['yes','no'])
        if res == 'no':
            print('cancel the version bumps.')
            return

        self._update_version( ver )
        res = prompt('''

        ========================================================
        bump the version %s => %s
        please check below files 

        src/addon/src/version.h
        conanfile.py
        docs/release-notes.md
        yes => commit and tag this release
        no => give up the commit, you have to revert change file manually.

        '''%(oldver,ver), ['yes','no'])
        if res == 'yes':
            call('git commit -a -m "bumps to version %s"'%ver)
            call('git tag v%s -m "bumps to version %s"'%(ver,ver))


    def _has_uncommit(self):
        out,err = check_call('git status -s --show-stash')
        out = out.strip('\n')
        if out:            
            return True
        return False




    def run(self, argv):
        if len(argv) == 0:
            argv = ['build']
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers()
        
        # create the parser for the "foo" command
        builder = subparsers.add_parser('build')
        builder.add_argument('--with-nvm', type=bool, default=False)        
        builder.set_defaults(func=self._build)
        
        # create the parser for the "bar" command
        bump_version = subparsers.add_parser('bump-version')
        bump_version.add_argument('release', choices=['major', 'minor', 'patch'])
        bump_version.set_defaults(func=self._bump_version)
        
        # parse the args and call whatever function was selected
        args = parser.parse_args(argv)
        args.func(args)


if __name__ == '__main__':   
    rm =ReleaseManager()
    rm.run( sys.argv[1:] )











































#import platform
#import os
#import sys
#import copy
#import re
#import subprocess
#import shlex
#import platform
#import semver
#
#from bincrafters import build_template_default
#
#def load_version():
#    filename = os.path.join(os.path.dirname(__file__), 'addon/src/version.h')
#
#    with open(filename, "rt") as version_file:
#        content = version_file.read()
#        version = re.search(r'#define __VERSION__\s+"([0-9a-z.-]+)"', content).group(1)
#        return version
#
#def load_conanfile_version():
#    filename = os.path.join(os.path.dirname(__file__), 'conanfile.py')
#
#    with open(filename, "rt") as version_file:
#        content = version_file.read()
#        version = re.search(r'''version\s*=\s*["'](\S*)["']''', content).group(1)
#        return version
#
#def bump_version(release='patch'):
#    version = ver or load_version()
#    Ver = semver.SemVer( ver or load_conanfile_version())
#    #bumps old ver to new version
#    version = Ver.inc( release )
#
#    filename = os.path.join(os.path.dirname(__file__), 'addon/src/version.h')
#    f = open(filename,'w');
#    f.write( '#define __VERSION__ "%s"'%version)
#    f.close()
#
#    
#
#
#
#
#    with open(filename, "w") as version_file:
#        content = version_file.read()
#        version = re.search(r'#define __VERSION__\s+"([0-9a-z.-]+)"', content).group(1)
#        return version
#
#def build():
#    builder = build_template_default.get_builder()
#
#    items = []
#    for item in builder.items:
#        if not item.options["plugin.node:shared"]:
#           continue
#
#        # Visual Sutido 2017 only
#        if not (platform.system() == "Windows" and item.settings["compiler"] == "Visual Studio" and
#                item.settings["compiler.version"] == '15' ):
#            continue
#    
#        # skip mingw cross-builds
#        if not (platform.system() == "Windows" and item.settings["compiler"] == "gcc" and
#                item.settings["arch"] == "x86"):
#            items.append(item)
#        
#
#    builder.items = items
#
#    builder.run()
#
#
#def build_with_nvm():
#    try:
#        import devutils
#        import devutils.software        
#    except:
#        raise Exception('Please install devutils < pip install devutils >.')
#        
#    
#    os.environ['CONAN_BUILD_TYPES']='Release'
#    archs = ['x86_64','x86']
#    for arch in archs:
#        os.environ['CONAN_ARCHS']=arch
#        sys.path.insert(0, os.path.dirname(__file__)+'/devutils')        
#        
#        nvm = devutils.software.NodeVersioManager()
#        nvm.use( arch, '^8.11')
#        build()
#        return
#
#if __name__ == "__main__":
#    if os.environ.get('CONAN_STABLE_BRANCH_PATTERN',None) is None:
#        os.environ['CONAN_STABLE_BRANCH_PATTERN'] = 'master'
#    if platform.system() == 'Windows' and os.environ.get('CONAN_VISUAL_VERSIONS',None) is None:
#        os.environ['CONAN_VISUAL_VERSIONS'] = '15'
#
#
#    if len(sys.argv) >1 and sys.argv[1]=='nvm':
#        build_with_nvm()
#    else:
#        build()

