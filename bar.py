# -*- coding: utf-8 -*-
import re
from natto import MeCab

s1 = 'にわにはにわにわとりがいる。'

p1 = 'にわ|はにわにわとり'


with MeCab() as nm:
    #print(nm.parse(s1))
    #print('-----')
    print(nm.parse(s1, morpheme_constraints=p1))
