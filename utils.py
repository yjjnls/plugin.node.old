from __future__ import print_function

import os
import sys
import platform

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

def is_same_dir(a,b):
    def normpath( p ):
        return os.path.normpath( 
            os.path.abspath(p) ).replace('\\','/')
    return normpath(a) == normpath(b)


def admin_win32(filename):
    import ctypes, sys

    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    if not is_admin():
        if sys.version_info[0] == 3:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, filename, None, 1)
        else:#in python2.x
            ctypes.windll.shell32.ShellExecuteW(None, u"runas", unicode(sys.executable), unicode(filename), None, 1)

def admin( filename ):
    if platform.system() == "Windows":
        admin_win32(filename)

import re
_PATTERN_VERSION=re.compile(r'^(?P<version>\d+\.\d+\.\d+)$')
_PATTERN_CURRENT=re.compile(r'^\*\s*(?P<version>\d+\.\d+\.\d+)\s*\(Currently using (?P<arch>\d+)-bit executable\)$')

def node( major, arch):
    if isinstance(major, int):
        major = str(major)

    nodes=set()
    current=None
    versions , unused = check_call('nvm list')
    for version in versions.split('\n'):
        version = version.decode('utf8').strip()
        m = _PATTERN_CURRENT.match(version)
        if m:
            current =(m.group('version'),m.group('arch'))
            nodes.add(m.group('version'))
            continue

        m = _PATTERN_VERSION.match(version)
        if m:
            nodes.add(m.group('version'))
            continue

    _ARCHs={'x86': '32','x86_64':'64','x64':'64'}

    v,a = current
    if v.startswith(major) and a == _ARCHs[arch]:
        return

    for ver in nodes:
        if ver.startswith(major):
            check_call( 'nvm use %s %s'%(ver,_ARCHs[arch]))
            return
    else:
        raise Exception("not install nodejs %s %s"%(major,arch))

    raise Exception("canot active nodejs %s %s"%(major,arch))


class Platform:
    ''' Enumeration of supported platforms '''
    LINUX = 'linux'
    WINDOWS = 'windows'
    DARWIN = 'darwin'
    ANDROID = 'android'
    IOS = 'ios'


class Architecture:
    ''' Enumeration of supported acrchitectures '''
    X86 = 'x86'
    X86_64 = 'x86_64'
    UNIVERSAL = 'universal'
    ARM = 'arm'
    ARMv7 = 'armv7'
    ARMv7S = 'armv7s'
    ARM64 = 'arm64'


class NodeJS(object):

    def __init__(self, home = None):
        '''
        '''
        self._home = home

    def arch(self):
        _map={'ia32':Architecture.X86,'x64':Architecture.X86_64}
        out ,err = check_call('node -p os.arch()',self._home)
        return _map[out.strip()]

    def version(self):
        out ,err = check_call('node --version',self._home)
        return out.strip()[1:]

    def platform(self):
        _map={'win32':Platform.WINDOWS,'linux':Platform.LINUX,
        'darwin':Platform.DARWIN}
        out ,err = check_call('node -p os.platform()',self._home)
        return _map[out.strip()]

class NodeVersioManager(obj):

    def __init__(self,home=None):
        '''
        '''
        self._home = home

    def use(self, arch, version=None,major=None,minor=None)

nodejs = NodeJS()
print(nodejs.arch(),nodejs.platform(),nodejs.version())
