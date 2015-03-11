# -*- coding: utf-8 -*-
import re
import MeCab
from MeCab import MECAB_ANY_BOUNDARY, MECAB_INSIDE_TOKEN, MECAB_TOKEN_BOUNDARY

DICINFO_KEYS = ('charset', 'filename', 'lsize', 'rsize', 'size', 'type', 'version')

class Tagger(MeCab.Tagger):

    # not needed, as you already have MeCabEnv.charset
    def dictionary_info(self):
        info = MeCab._MeCab.Tagger_dictionary_info(self)
        return {key: getattr(info, key) for key in DICINFO_KEYS}

    def split_sentence(self, sentence, pattern):
        # sentence and pattern should be unicode!
        last_found_position = 0
        #for m in re.finditer(pattern, sentence, re.U):
        for m in re.finditer(pattern, sentence):
            if last_found_position < m.start():
                yield (sentence[last_found_position:m.start()], False)
                last_found_position = m.start()
            yield (sentence[last_found_position:m.end()], True)
            last_found_position = m.end()
        if last_found_position < len(sentence):
            yield (sentence[last_found_position:], False)

    def boundary_constraint_parse(self, sentence, pattern='.', any_boundary=False):
        lattice = MeCab.Lattice()
        lattice.set_sentence(''.join(sentence))
        if any_boundary:
            default_boundary_constraint = MECAB_ANY_BOUNDARY
        else:
            default_boundary_constraint = MECAB_INSIDE_TOKEN

        byte_position = 0
        lattice.set_boundary_constraint(byte_position, MECAB_TOKEN_BOUNDARY)

        charset = self.dictionary_info()['charset']
        for (token, match) in self.split_sentence(sentence, pattern):
            print("token: {}".format(token))
            byte_position += 1
            if match:
                boundary_constraint = MECAB_INSIDE_TOKEN
            else:
                boundary_constraint = default_boundary_constraint
            for i in range(1, len(token.encode(charset))):
            #for i in range(1, len(token)):
                lattice.set_boundary_constraint(byte_position, boundary_constraint)
                byte_position += 1
            lattice.set_boundary_constraint(byte_position, MECAB_TOKEN_BOUNDARY)
        
        if self.parse(lattice):
            return lattice.toString()

    def foo(self, sentence, pattern='.', any_boundary=False):
        lattice = MeCab.Lattice()
        lattice.set_request_type(1)     # MECAB_ONE_BEST
        #lattice.set_request_type(2)     # MECAB_NBEST
        print("type? {}".format(type(sentence)))
        text = ''.join(sentence)
        print("type(text)? {}".format(type(sentence)))
        lattice.set_sentence(text)
        if any_boundary:
            default_boundary_constraint = MECAB_ANY_BOUNDARY
        else:
            default_boundary_constraint = MECAB_INSIDE_TOKEN

        byte_position = 0
        lattice.set_boundary_constraint(byte_position, MECAB_TOKEN_BOUNDARY)

        charset = self.dictionary_info()['charset']
        for (token, match) in self.split_sentence(sentence, pattern):
            print("token: {}".format(token))
            byte_position += 1
            if match:
                boundary_constraint = MECAB_INSIDE_TOKEN
            else:
                boundary_constraint = default_boundary_constraint
            for i in range(1, len(token.encode(charset))):
            #for i in range(1, len(token)):
                lattice.set_boundary_constraint(byte_position, boundary_constraint)
                byte_position += 1
            lattice.set_boundary_constraint(byte_position, MECAB_TOKEN_BOUNDARY)

        self.parse(lattice)
        l = lattice.size()

        print("Lattice size: {}".format(l))
        print("Lattice available?: {}".format(lattice.is_available()))

        b = lattice.bos_node()
        while b:
            print("node id: {}, surface: {}, feature: {}, stat: {}".format(b.id, b.surface, b.feature, b.stat))
            b = b.next
        print('------------')

        #for _ in range(2):
        #    check = lattice.next()
        #    print("check? {}".format(check))
        #    if check:
        #        b = lattice.bos_node()
        #        while b:
        #            print "node id: {}".format(b.id)
        #            #print "surface: {}; feature: {}".format(b.surface, b.feature)
        #            #print "- isbest: {}, wcost: {}, cost: {}".format(b.isbest, b.wcost, b.cost)
        #            b = b.next
        #        print '------------'

if __name__ == '__main__':
    tagger = Tagger()
    print('形態素境界制約付き解析\n')

    #text = 'ポエム読むならQiita最高'
    #patt = '[a-zA-Z0-9\s\-]+'
    text = 'にわにはにわにわとりがいる。' 
    patt = 'にわ|はにわにわとり'
    #
    text2 = '東京メトロで帰る。' 
    patt2 = '東京メトロ'
    #
    text3 = '88 JPは買いです。' 
    patt3 = '[\d]{2,}[\s]+JP'
    #
    text4 = 'にわにはにわにわとりがいる。'
    patt4 = 'にわ|はにわにわとり'


    print('original text: {}'.format(text))
    print()
    #print tagger.parse(text)
    print('------------')
    print()
    #print 'boundary-constraint'
    #for t in tagger.split_sentence(text, patt):
    #    print(t[0])
    #print
    #print(tagger.boundary_constraint_parse(text, patt, any_boundary=True))
    #print '------------'
    #print

    print('boundary-constraint, node-parsing')
    tagger.foo(text, patt, any_boundary=True)
    print()
    tagger.foo(text2, patt2, any_boundary=True)
    print()
    tagger.foo(text3, patt3, any_boundary=True)
    print()
    tagger.foo(text4, patt4, any_boundary=True)



