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

    Also attempts to locate and obtain the full path to the MeCab library.

    This makes invocations to the mecab and mecab-config (not available on
    Windows) executables.

    Will defer to the user-provided values in environment variables
    MECAB_PATH and MECAB_CHARSET.
    '''
    MECAB_PATH = 'MECAB_PATH'
    MECAB_CHARSET = 'MECAB_CHARSET'

    _WINLIB_EXT = 'dll'
    _MACLIB_EXT = 'dylib'

    _UNIXLIB_EXT = 'so'
    _INFO_EUCJP_DEFAULT = 'INFO: defaulting MeCab charset to euc-jp'
    _INFO_SJIS_DEFAULT = 'INFO: defaulting MeCab charset to shift-jis'
    _INFO_UTF8_DEFAULT = 'INFO: defaulting MeCab charset to utf-8'
    _ERROR_NODIC = 'ERROR: MeCab dictionary charset not found'
    _ERROR_NOCMD = 'ERROR: mecab -D command not recognized'
    _ERROR_NOLIB = 'ERROR: %s could not be found, please use MECAB_PATH'
    _ERROR_MECABD = 'ERROR: mecab -D could not be used to locate %s'
    _ERROR_MECABCONFIG = 'ERROR: mecab-config could not locate %s'

    def __init__(self):
        '''Initializes the MeCabEnv instance.

        Raises:
            EnvironmentError: A problem in obtaining the system dictionary info
                was encountered.
        '''
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
            return cset
        else:
            try:
                res = Popen(['mecab', '-D'], stdout=PIPE).communicate()
                lines = res[0].decode()
                if not lines.startswith('unrecognized'):
                    dicinfo = lines.split(os.linesep)
                    t = [t for t in dicinfo if t.startswith('charset')]
                    if len(t) > 0:
                        return t[0].split()[1].lower()
                    else:
                        sys.stderr.write('%s\n' % self._ERROR_NODIC)
                        raise EnvironmentError(self._ERROR_NODIC)
                else:
                    sys.stderr.write('%s\n' % self._ERROR_NOCMD)
                    raise EnvironmentError(self._ERROR_NOCMD)
            except OSError:
                if sys.platform == 'win32':
                    sys.stderr.write('%s\n' % self._INFO_SJIS_DEFAULT)
                    return 'shift-jis'
                elif sys.platform == 'darwin':
                    sys.stderr.write('%s\n' % self._INFO_UTF8_DEFAULT)
                    return 'utf-8'
                else:
                    sys.stderr.write('%s\n' % self._INFO_EUCJP_DEFAULT)
                    return 'euc-jp'

    def __get_libpath(self):
        '''Return the full path to the MeCab library.

        On Windows, the path to the system dictionary is used to deduce the
        path to libmecab.dll.

        Otherwise, mecab-config is used find the libmecab shared object or
        dynamic library (*NIX or Mac OS, respectively).

        Will defer to the user-specified MECAB_PATH environment variable, if
        set.

        Returns:
            The full path to the MeCab library.

        Raises:
            EnvironmentError: A problem was encountered in trying to locate the
                MeCab library.
        '''
        libp = os.getenv(self.MECAB_PATH)
        if libp:
            return libp
        else:
            plat = sys.platform
            if plat == 'win32':
                lib = 'libmecab.%s' % self._WINLIB_EXT
                try:
                    cmd = ['mecab', '-D']
                    res = Popen(cmd, stdout=PIPE).communicate()
                    lines = res[0].decode()
                    if not lines.startswith('unrecognized'):
                        dicinfo = lines.split(os.linesep)
                        t = [t for t in dicinfo if t.startswith('filename')]
                        if len(t) > 0:
                            ldir = t[0].split('etc')[0][10:].strip()
                            libp = os.path.join(ldir, 'bin', lib)
                        else:
                            raise EnvironmentError(self._ERROR_MECABD % lib)
                    else:
                        raise EnvironmentError(self._ERROR_MECABD % lib)
                except EnvironmentError:
                    sys.stderr.write('%s\n' % sys.exc_info()[0])
                    raise EnvironmentError(self._ERROR_NOLIB % lib)
            else:
                # UNIX-y OS?
                if plat == 'darwin':
                    lib = 'libmecab.%s' % self._MACLIB_EXT
                else:
                    lib = 'libmecab.%s' % self._UNIXLIB_EXT

                try:
                    cmd = ['mecab-config', '--libs-only-L']
                    res = Popen(cmd, stdout=PIPE).communicate()
                    lines = res[0].decode()
                    if not lines.startswith('unrecognized'):
                        linfo = lines.strip()
                        libp = os.path.join(linfo, lib)
                    else:
                        raise EnvironmentError(self._ERROR_MECABCONFIG % lib)
                except EnvironmentError:
                    sys.stderr.write('%s\n' % sys.exc_info()[0])
                    raise EnvironmentError(self._ERROR_NOLIB % lib)

            if libp and os.path.exists(libp):
                os.environ[self.MECAB_PATH] = libp
                return libp
            else:
                raise EnvironmentError(self._ERROR_NOLIB % libp)


'''
Copyright (c) 2014, Brooke M. Fujita.
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
