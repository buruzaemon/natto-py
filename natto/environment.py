# -*- coding: utf-8 -*-
'''Convenience API to obtain information on MeCab environment.'''
import os
import sys

from subprocess import Popen, PIPE

class MeCabEnv(object):
    '''Convenience class of object to obtain information on MeCab environment.

    This will attempt to obtain the character encoding (charset) of MeCab's
    system dictionary, which will determine the encoding used when passing
    strings in and obtaining string results from MeCab.

    Also attempts to locate and obtain the absolute path to the MeCab library.

    This makes invocations to the mecab and mecab-config (not available on
    Windows) executables.

    Will defer to the user-provided values in environment variables
    MECAB_PATH and MECAB_CHARSET.

    The debug keyword argument outputs debugging messages to stderr.
    '''
    MECAB_PATH = 'MECAB_PATH'
    MECAB_CHARSET = 'MECAB_CHARSET'

    _LIBMECAB = 'libmecab.{}'
    _MACLIB_EXT = 'dylib'
    _UNIXLIB_EXT = 'so'
    _WINLIB_EXT = 'dll'
    _WINHKEY = r'HKEY_CURRENT_USER\Software\MeCab'
    _WINVALUE = 'mecabrc'

    _DEBUG_CSET_DEFAULT = 'DEBUG: defaulting MeCab charset to {}\n'
    _ERROR_NODIC = 'ERROR: MeCab dictionary charset not found'
    _ERROR_NOCMD = 'ERROR: mecab -D command not recognized'
    _ERROR_NOLIB = 'ERROR: {} could not be found, please use MECAB_PATH'
    _ERROR_WINREG = 'ERROR: No value {} in Windows Registry at {}'
    _ERROR_MECABCONFIG = 'ERROR: mecab-config could not locate {}'

    def __init__(self, **kwargs):
        '''Initializes the MeCabEnv instance.

        Kwargs:
            debug (bool): Flag for outputting debug messages to stderr.

        Raises:
            EnvironmentError: A problem in obtaining the system dictionary info
                was encountered.
        '''
        self.debug = False
        if 'debug' in kwargs.keys():
            self.debug = kwargs['debug']
        self.charset = self.__get_charset()
        self.libpath = self.__get_libpath()

    def __get_charset(self):
        '''Return the character encoding (charset) used internally by MeCab.

        Charset is that of the system dictionary used by MeCab. Will defer to
        the user-specified MECAB_CHARSET environment variable, if set.

        Defaults to shift-jis on Windows.
        Defaults to utf-8 on Mac OS.
        Defaults to euc-jp, as per MeCab documentation, when all else fails.

        Returns:
            Character encoding (charset) used by MeCab.
        '''
        cset = os.getenv(self.MECAB_CHARSET)
        if cset:
            if self.debug:
                sys.stderr.write(self._DEBUG_CSET_DEFAULT.format(cset))
            return cset
        else:
            try:
                res = Popen(['mecab', '-D'], stdout=PIPE).communicate()
                lines = res[0].decode()
                if not lines.startswith('unrecognized'):
                    dicinfo = lines.split(os.linesep)
                    t = [t for t in dicinfo if t.startswith('charset')]
                    if len(t) > 0:
                        cset = t[0].split()[1].lower()
                        if self.debug:
                            sys.stderr.write(
                                self._DEBUG_CSET_DEFAULT.format(cset))
                        return cset
                    else:
                        sys.stderr.write('{}\n'.format(self._ERROR_NODIC))
                        raise EnvironmentError(self._ERROR_NODIC)
                else:
                    sys.stderr.write('{}\n'.format(self._ERROR_NOCMD))
                    raise EnvironmentError(self._ERROR_NOCMD)
            except OSError:
                cset = 'euc-jp'
                if sys.platform == 'win32':
                    cset = 'shift-jis'
                elif sys.platform == 'darwin':
                    cset = 'utf8'
                if self.debug:
                    sys.stderr.write(self._DEBUG_CSET_DEFAULT.format(cset))
                return cset

    def __get_libpath(self):
        '''Return the absolute path to the MeCab library.

        On Windows, the path to the system dictionary is used to deduce the
        path to libmecab.dll.

        Otherwise, mecab-config is used find the libmecab shared object or
        dynamic library (*NIX or Mac OS, respectively).

        Will defer to the user-specified MECAB_PATH environment variable, if
        set.

        Returns:
            The absolute path to the MeCab library.

        Raises:
            EnvironmentError: A problem was encountered in trying to locate the
                MeCab library.
        '''
        libp = os.getenv(self.MECAB_PATH)
        if libp:
            return os.path.abspath(libp)
        else:
            plat = sys.platform
            if plat == 'win32':
                lib = self._LIBMECAB.format(self._WINLIB_EXT)

                try:
                    v = self.__regkey_value(self._WINHKEY, self._WINVALUE)
                    ldir = v.split('etc')[0]
                    libp = os.path.join(ldir, 'bin', lib)
                except EnvironmentError as err:
                    sys.stderr.write('{}\n'.format(err))
                    sys.stderr.write('{}\n'.format(sys.exc_info()[0]))
                    raise EnvironmentError(
                        self._ERROR_WINREG.format(self._WINVALUE,
                                                  self._WINHKEY))
            else:
                # UNIX-y OS?
                if plat == 'darwin':
                    lib = self._LIBMECAB.format(self._MACLIB_EXT)
                else:
                    lib = self._LIBMECAB.format(self._UNIXLIB_EXT)

                try:
                    cmd = ['mecab-config', '--libs-only-L']
                    res = Popen(cmd, stdout=PIPE).communicate()
                    lines = res[0].decode()
                    if not lines.startswith('unrecognized'):
                        linfo = lines.strip()
                        libp = os.path.join(linfo, lib)
                    else:
                        raise EnvironmentError(
                            self._ERROR_MECABCONFIG.format(lib))
                except EnvironmentError as err:
                    sys.stderr.write('{}\n'.format(err))
                    sys.stderr.write('{}\n'.format(sys.exc_info()[0]))
                    raise EnvironmentError(self._ERROR_NOLIB.format(lib))

            if libp and os.path.exists(libp):
                libp = os.path.abspath(libp)
                os.environ[self.MECAB_PATH] = libp
                return libp
            else:
                raise EnvironmentError(self._ERROR_NOLIB.format(libp))

    def __regkey_value(self, path, name='', start_key=None):
        r'''Return the data of value mecabrc at MeCab HKEY node.

        On Windows, the path to the mecabrc as set in the Windows Registry is
        used to deduce the path to libmecab.dll.

        Returns:
            The full path to the mecabrc on Windows.

        Raises:
            WindowsError: A problem was encountered in trying to locate the
                value mecabrc at HKEY_CURRENT_USER\Software\MeCab.
        '''
        if sys.version < '3':
            import _winreg as reg
        else:
            import winreg as reg

        def _fn(path, name='', start_key=None):
            if isinstance(path, str):
                path = path.split('\\')
            if start_key is None:
                start_key = getattr(reg, path[0])
                return _fn(path[1:], name, start_key)
            else:
                subkey = path.pop(0)
            with reg.OpenKey(start_key, subkey) as handle:
                if path:
                    return _fn(path, name, handle)
                else:
                    desc, i = None, 0
                    while not desc or desc[0] != name:
                        desc = reg.EnumValue(handle, i)
                        i += 1
                    return desc[1]
        return _fn(path, name, start_key)

'''
Copyright (c) 2015, Brooke M. Fujita.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

 * Redistributions of source code must retain the above
   copyright notice, this list of conditions and the
   following disclaimer.

 * Redistributions in binary form must reproduce the above
   copyright notice, this list of conditions and the
   following disclaimer in the documentation and/or other
   materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''
