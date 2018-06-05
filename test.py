from __future__ import absolute_import, division, print_function
import sys
import os
import re
import semver
import devutils
import argparse
from devutils.shell import check_call,prompt


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
    
    def bump_version(self, release = 'patch'):
        pass


    def _update_version( self, version ):
        filename = os.path.join(os.path.dirname(__file__), 'addon/src/version.h')
        f = open(filename, 'wb')
        f.write(r'#define __VERSION__ "%s"'%version + '\n')
        f.close()

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

        from devutils import shell
        shell.replace('docs/release-notes.md',{'${__version__}':version})

    def buildno(self):
        return self._get_last_tag_commit_count()


    def parse(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("command")


    def _build(self,args):
        print ('RUN build')

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
        if res == 'no':
            return

        check_call('git commit -m bumps to version %s'%ver)
        check_call('git tag v%s -m bumps to version %s'%(ver,ver))


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

        





        


#rm = ReleaseManager()
#
##rm._update_version("1.2.3.4s")
#
##rm._get_commit_count()
##semver.inc('1.2.3-dev.')
#print '---------------------'
#print rm.buildno()
#print rm._get_last_tag()
#print rm._get_tag_commit_id( rm._get_last_tag())
#print '---------------------'


if __name__ == '__main__':    
    rm =ReleaseManager()
    rm.run( sys.argv[1:] )
    #import argparse
    #import sys
    #print sys.argv
    #
    #parser = argparse.ArgumentParser()
    #parser.add_argument("echo",default = None)
    #args = parser.parse_args(sys.argv[1:])
    #print args.echo
    