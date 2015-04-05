# -*- coding: utf-8 -*-
import MeCab

class Tagger(MeCab.Tagger):

    def feature_constraint_parse(self):
        lattice = MeCab.Lattice()
        #sentence = 'これは初心で大人気である。'
        sentence = 'くぅ〜マミさんの紅茶めちゃウマっすよ〜'
        lattice.set_sentence(sentence)

        #lattice.set_feature_constraint(0, 6, "*")
        #lattice.set_feature_constraint(6, 9, "*")
        #lattice.set_feature_constraint(9, 15, "その他")
        #lattice.set_feature_constraint(15, 18, "*")
        #lattice.set_feature_constraint(18, 27, "感動詞")
        #lattice.set_feature_constraint(27, 30, "*")
        #lattice.set_feature_constraint(30, 36, "*")
        #lattice.set_feature_constraint(36, 39, "*")
        lattice.set_feature_constraint(0, 9, "感動詞")
        lattice.set_feature_constraint(9, 21, "hoge他")
        lattice.set_feature_constraint(51, 57, "その変")

        self.parse(lattice)

        node = lattice.bos_node()
        while node:
            yield node
            node = node.next

if __name__ == '__main__':
    tagger = Tagger('-p -N3')
    #tagger = Tagger()
    for n in tagger.feature_constraint_parse():
        print("{} -- {}".format(n.surface, n.feature))
