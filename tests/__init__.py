import os
import sys
from natto.mecab import MeCab
from subprocess import Popen, PIPE

# full path to MeCab library is required for testing...
if not os.getenv(MeCab.MECAB_PATH):
    raise EnvironmentError('Please set MECAB_PATH before running the tests')
# as well as the character encoding used internally by MeCab...
if not os.getenv(MeCab.MECAB_CHARSET):
    raise EnvironmentError('Please set MECAB_CHARSET before running the tests')

# and the mecab executable is invoked during the tests...
try:
    res = Popen(['mecab', '-h'], stdout=PIPE).communicate()
    line = res[0]
    exp = 'MeCab'
    if sys.version >= '3':
        line = line.decode(os.getenv(MeCab.MECAB_CHARSET))
    if not line.startswith(exp):
        raise EnvironmentError('Please check your mecab installation')
except StandardError as err:
    raise EnvironmentError(err)