import os
import re
import semver

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

    def _get_commit_count(self):

        out,err = check_call('git log --since="Oct 27 9:16:10 2017 +0800"  --pretty=oneline')
        print out
        print len(out.split('\n'))




        


rm = ReleaseManager()

#rm._update_version("1.2.3.4s")

rm._get_commit_count()
semver.inc('1.2.3-dev.')