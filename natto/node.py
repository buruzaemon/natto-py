# -*- coding: utf-8 -*-
'''Wrapper for MeCab node.'''

class MeCabNode(object):
    '''Representation of a MeCab Node struct.

    A list of MeCab nodes is returned when parsing a string of Japanese with
    as_nodes=True. Each node will contain detailed information about the
    morpheme encompassed.

    :ivar ptr: This node's pointer.
    :ivar prev: Pointer to previous node.
    :ivar next: Pointer to next node.
    :ivar enext: Pointer to the node which ends at the same position.
    :ivar bnext: Pointer to the node which starts at the same position.
    :ivar rpath: Pointer to the right path; None if MECAB_ONE_BEST mode.
    :ivar lpath: Pointer to the right path; None if MECAB_ONE_BEST mode.
    :ivar surface: Surface string, Unicode.
    :ivar feature: Feature string, Unicode.
    :ivar nodeid: Unique node id.
    :ivar length: Length of surface form.
    :ivar rlength: Length of the surface form including leading white space.
    :ivar rcattr: Right attribute id.
    :ivar lcattr: Left attribute id.
    :ivar posid: Part-of-speech id.
    :ivar char_type: Character type.
    :ivar stat: Node status; 0 (NOR), 1 (UNK), 2 (BOS), 3 (EOS), 4 (EON).
    :ivar isbest: 1 if this node is best node.
    :ivar alpha: Forward accumulative log summation (with marginal probability).
    :ivar beta: Backward accumulative log summation (with marginal probability).
    :ivar prob: Marginal probability, only with marginal probability flag.
    :ivar wcost: Word cost.
    :ivar cost: Best accumulative cost from bos node to this node.

    Example usage::

        from natto import MeCab

        text = '卓球なんて死ぬまでの暇つぶしだよ。'

        # Ex. basic node parsing
        #
        with MeCab() as nm:
            for n in nm.parse(text, as_nodes=True):
        ...     # ignore the end-of-sentence nodes
        ...     if not n.is_eos():
        ...         # output the morpheme surface and default ChaSen feature
        ...         print('{}\\t{}'.format(n.surface, n.feature))
        ...
        卓球    名詞,サ変接続,*,*,*,*,卓球,タッキュウ,タッキュー
        なんて  助詞,副助詞,*,*,*,*,なんて,ナンテ,ナンテ
        死ぬ    動詞,自立,*,*,五段・ナ行,基本形,死ぬ,シヌ,シヌ
        まで    助詞,副助詞,*,*,*,*,まで,マデ,マデ
        の      助詞,連体化,*,*,*,*,の,ノ,ノ
        暇つぶし        名詞,一般,*,*,*,*,暇つぶし,ヒマツブシ,ヒマツブシ
        だ      助動詞,*,*,*,特殊・ダ,基本形,だ,ダ,ダ
        よ      助詞,終助詞,*,*,*,*,よ,ヨ,ヨ
        。      記号,句点,*,*,*,*,。,。,。

        # Ex. custom node format
        #
        # -F         ... short-form of --node-format
        # %F,[6,7,0] ... extract these elements from ChaSen feature as CSV
        #                - morpheme root-form (6th index)
        #                - reading (7th index)
        #                - part-of-speech (0th index)
        # %h         ... part-of-speech ID (IPADIC)
        #
        # -U         ... short-form of --unk-format
        #                specify empty CSV ,,, when morpheme cannot be found
        #                in dictionary
        #
        with MeCab(r'-F%F,[6,8,0],%h\\n -U,,,\\n') as nm:
            for n in nm.parse(text, as_nodes=True):
        ...     # ignore the end-of-sentence nodes
        ...     if not n.is_eos():
        ...         # output custom-formatted node feature
        ...         print(n.feature)
        ...
        卓球,タッキュウ,名詞,36
        なんて,ナンテ,助詞,21
        死ぬ,シヌ,動詞,31
        まで,マデ,助詞,21
        の,ノ,助詞,24
        暇つぶし,ヒマツブシ,名詞,38
        だ,ダ,助動詞,25
        よ,ヨ,助詞,17
        。,。,記号,7

    '''
    _REPR_FMT = '<{}.{} node={}, stat={}, surface="{}", feature="{}">'

    # Normal MeCab node defined in the dictionary.
    NOR_NODE = 0
    # Unknown MeCab node not defined in the dictionary.
    UNK_NODE = 1
    # Virtual node representing the beginning of the sentence.
    BOS_NODE = 2
    # Virtual node representing the end of the sentence.
    EOS_NODE = 3
    # Virtual node representing the end of an N-Best MeCab node list.
    EON_NODE = 4

    def __init__(self, nptr, surface, feature):
        '''Initializes the MeCab node and its attributes.'''
        self.ptr = nptr
        self.prev = nptr.prev
        self.next = getattr(nptr, 'next')
        self.enext = nptr.enext
        self.bnext = nptr.bnext
        self.rpath = nptr.rpath
        self.lpath = nptr.lpath
        self.surface = surface
        self.feature = feature
        self.nodeid = nptr.id
        self.length = nptr.length
        self.rlength = nptr.rlength
        self.rcattr = nptr.rcAttr
        self.lcattr = nptr.lcAttr
        self.posid = nptr.posid
        self.char_type = nptr.char_type
        self.stat = nptr.stat
        self.isbest = nptr.isbest
        self.alpha = nptr.alpha
        self.beta = nptr.beta
        self.prob = nptr.prob
        self.wcost = nptr.wcost
        self.cost = nptr.cost

    def is_nor(self):
        '''Is this a normal node, defined in a dictionary?

        :return: True if normal node, False otherwise.
        '''
        return self.stat == self.NOR_NODE

    def is_unk(self):
        '''Is this an unknown node, not defined in any dictionary?

        :return: True if unknown node, False otherwise.
        '''
        return self.stat == self.UNK_NODE

    def is_bos(self):
        '''Is this a beginning-of-sentence node?

        :return: True if beginning-of-sentence node, False otherwise.
        '''
        return self.stat == self.BOS_NODE

    def is_eos(self):
        '''Is this an end-of-sentence node?

        :return: True if end-of-sentence node, False otherwise.
        '''
        return self.stat == self.EOS_NODE

    def is_eon(self):
        '''Is this an end of an N-best node list?

        :return: True if end of an N-best node list, False otherwise.
        '''
        return self.stat == self.EON_NODE

    def __repr__(self):
        '''Return a string representation of this MeCab node.

        :return: str - string representation.
        '''
        return self._REPR_FMT.format(type(self).__module__,
                                     type(self).__name__,
                                     self.ptr,
                                     self.stat,
                                     self.surface,
                                     self.feature)

'''
Copyright (c) 2019, Brooke M. Fujita.
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
