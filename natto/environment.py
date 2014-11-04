# -*- coding: utf-8 -*-
import os
import sys
from subprocess import Popen, PIPE

class MeCabEnv(object):

    MECAB_PATH = 'MECAB_PATH'
    MECAB_CHARSET = 'MECAB_CHARSET'

    _WINLIB_EXT = "dll"
    _MACLIB_EXT = "dylib"
    _UNIXLIB_EXT = "so"

    _INFO_SJIS_DEFAULT = "INFO: defaulting MeCab charset to shift-jis"
    _INFO_EUCJP_DEFAULT = "INFO: defaulting MeCab charset to euc-jp"
    _ERROR_NODIC = "ERROR: MeCab dictionary charset not found"
    _ERROR_NOCMD = "ERROR: mecab -D command not recognized"
    _ERROR_NOLIB = "ERROR: %s could not be found, please use MECAB_PATH"

    def __init__(self):
        self.charset = self.__get_charset()
        self.libpath = self.__get_libpath()

    def __get_charset(self):
        """Return the charset (character encoding) used internally by MeCab.
        #try MECAB_CHARSET first
        # try mecab -D next

        # default to euc-jp
        """
        cset = os.getenv(self.MECAB_CHARSET)
        if cset:
            return cset
        else:
            try:
                res = Popen(['mecab', '-D'], stdout=PIPE).communicate()
                if not res[0].startswith('unrecognized'):
                    dicinfo = res[0].split(os.linesep)
                    t = [t for t in dicinfo if t.startswith('charset')]
                    if len(t) > 0:
                        return t[0].split()[1].lower()
                    else:
                        sys.stderr.write("%s\n" % self._ERROR_NODIC)
                        raise EnvironmentError(self._ERROR_NODIC)
                else:
                    sys.stderr.write("%s\n" % self._ERROR_NOCMD)
                    raise EnvironmentError(self._ERROR_NOCMD)
            except:
                if sys.platform == 'win32':
                    sys.stderr.write("%s\n" % self._INFO_SJIS_DEFAULT)
                    return 'shift-jis'
                else:
                    sys.stderr.write("%s\n" % self._INFO_EUCJP_DEFAULT)
                    return 'euc-jp'

    def __get_libpath(self):
        libp = os.getenv(self.MECAB_PATH)
        if libp:
            return libp
        else:
            plat = sys.platform
            if plat == 'win32':
                lib = "libmecab.%s" % self._WINLIB_EXT
                try:
                    cmd = ['mecab', '-D']
                    res = Popen(cmd, stdout=PIPE).communicate()
                    if not res[0].startswith('unrecognized'):
                        dicinfo = res[0].split(os.linesep)
                        t = [t for t in dicinfo if t.startswith('filename')]
                        if len(t) > 0:
                            ldir = t[0].split('etc')[0][10:].strip()
                            libp = os.path.join(ldir, 'bin', lib)
                        else:
                            raise EnvironmentError("mecab -D could not be used to locate %s" % lib)
                    else:
                        raise EnvironmentError("Error invoking mecab")
                except:
                    raise EnvironmentError(self._ERROR_NOLIB % lib)
            else:
                # UNIX-y OS?
                if plat == 'darwin':
                    lib = "libmecab.%s" % self._MACLIB_EXT
                else:
                    lib = "libmecab.%s" % self._UNIXLIB_EXT

                try:
                    cmd = ['mecab-config', '--libs-only-L']
                    res = Popen(cmd, stdout=PIPE).communicate()
                    if not res[0].startswith('unrecognized'):
                        linfo = res[0].strip()
                        libp = os.path.join(linfo, lib)
                    else:
                        raise EnvironmentError("mecab-config could not locate %s" % lib)
                except:
                    raise EnvironmentError(self._ERROR_NOLIB % lib)

            if libp and os.path.exists(libp):
                os.environ[self.MECAB_PATH] = libp
                return libp
            else:
                raise EnvironmentError(self._ERROR_NOLIB % libp)
