# -*- coding: utf-8 -*-
class MeCabNode(object):
    """Representation of a MeCab node, wrapping the mecab_node_t struct.

    A list of MeCab nodes is returned when parsing a string of Japanese with
    as_nodes=True. Each node will contain detailed information about the
    morpheme encompassed.

    Attributes:
        ptr: This node's pointer.
        prev: Pointer to previous node.
        next: Pointer to next node.
        enext: Pointer to the node which ends at the same position.
        bnext: Pointer to the node which starts at the same position.
        rpath: Pointer to the right path; None if MECAB_ONE_BEST mode.
        lpath: Pointer to the right path; None if MECAB_ONE_BEST mode.
        surface: Surface string, Unicode.
        feature: Feature string, Unicode.
        nodeid: Unique node id.
        length: Length of surface form.
        rlength: Length of the surface form including leading white space.
        rcattr: Right attribute id.
        lcattr: Left attribute id.
        posid: Part-of-speech id.
        char_type: Character type.
        stat: Node status; 0 (NOR), 1 (UNK), 2 (BOS), 3 (EOS), 4 (EON).
        isbest: 1 if this node is best node.
        alpha: Forward accumulative log summation (with marginal probability).
        beta: Backward accumulative log summation (with marginal probability).
        prob: Marginal probability, only with marginal probability flag.
        wcost: Word cost.
        cost: Best accumulative cost from bos node to this node.

    Example usage:

        import natto

        nm = natto.MeCab()

        nodes = nm.parse('卓球なんて死ぬまでの暇つぶしだよ。', as_nodes=True)
        for n in nodes:
            if n.is_nor():
                print "%s\t%s" % (n.surface, n.cost)
    """

    _REPR_FMT = '<%s.%s pointer=%s, stat=%s, surface="%s", feature="%s">'

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
        """Initializes the MeCab node and its attributes."""
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
        """Returns True if this is a normal node (defined in dictionary)."""
        return self.stat == self.NOR_NODE

    def is_unk(self):
        """Returns True if this is an unknown node (not in dictionary)."""
        return self.stat == self.UNK_NODE

    def is_bos(self):
        """Returns True if this is a beginning-of-sentence node."""
        return self.stat == self.BOS_NODE

    def is_eos(self):
        """Returns True if this is an end-of-sentence node."""
        return self.stat == self.EOS_NODE

    def is_eon(self):
        """Returns True if this is an end of an N-best node list."""
        return self.stat == self.EON_NODE

    def __repr__(self):
        """Returns a string representation of this MeCab node."""
        return self._REPR_FMT % (type(self).__module__,
                                 type(self).__name__,
                                 self.ptr,
                                 self.stat,
                                 self.surface,
                                 self.feature)
