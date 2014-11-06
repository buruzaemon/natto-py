import os
from  natto.mecab import MeCab

if not os.getenv(MeCab.MECAB_PATH):
    raise EnvironmentError("Please set MECAB_PATH before running the tests")
if not os.getenv(MeCab.MECAB_CHARSET):
    raise EnvironmentError("Please set MECAB_CHARSET before running the tests")