# -*- coding: utf-8 -*-
"""The main API for using MeCab via natto-py."""
import argparse
import sys
from .binding import _ffi_libmecab
from .environment import MeCabEnv

class MeCab(object):
    """The main interface to the MeCab library, wrapping the MeCab Tagger.

    Instantiate this once, per any MeCab options you wish to use.
    This interface allows for parsing Japanese into simple strings of morpheme
    surface and related features, or for parsing as MeCab nodes which contain
    detailed information about the morphemes encompassed.

    Example usage:

        import natto

        nm = natto.MeCab()

        # output MeCab version
        print nm.version

        # output filename and charset for the MeCab system dictionary
        sysdic = nm.dicts[0]
        print sysdic.filename
        print sysdic.charset

        # parse a string
        print nm.parse('この星の一等賞になりたいの卓球で俺は、そんだけ！')

        # parse string into MeCab nodes,
        # and display much more detailed information about each morpheme
        nodes = nm.parse('飛べねえ鳥もいるってこった。', as_nodes=True)
        for n in nodes:
            if n.is_nor():
                print "%s\t%d\t%d" % (n.surface, n.posid, n.wcost)
    """

    MECAB_PATH = 'MECAB_PATH'
    MECAB_CHARSET = 'MECAB_CHARSET'

    _ERROR_PATH_UNSET = "Please set %s to the full path to MeCab library"
    _ERROR_INIT = "Could not initialize MeCab: %s"
    _ERROR_NULLPTR = "Could not initialize MeCab"
    _ERROR_EMPTY_STR = "Text to parse cannot be None"
    _ERROR_NOTUNICODE = "Text should be Unicode string"

    _REPR_FMT = '<%s.%s tagger="%s", options="%s", dicts=%s, version="%s">'

    _FN_NBEST_TOSTR = 'mecab_nbest_sparse_tostr'
    _FN_NBEST_TONODE = 'mecab_nbest_init'
    _FN_TOSTR = 'mecab_sparse_tostr'
    _FN_TONODE = 'mecab_sparse_tonode'

    # Mapping of mecab short-style configuration options to the `mecab`
    # tagger. See the `mecab` help for more details.
    _SUPPORTED_OPTS = {'-d' : 'dicdir',
                       '-u' : 'userdic',
                       '-l' : 'lattice_level',
                       '-O' : 'output_format_type',
                       '-a' : 'all_morphs',
                       '-N' : 'nbest',
                       '-p' : 'partial',
                       '-m' : 'marginal',
                       '-M' : 'max_grouping_size',
                       '-F' : 'node_format',
                       '-U' : 'unk_format',
                       '-B' : 'bos_format',
                       '-E' : 'eos_format',
                       '-S' : 'eon_format',
                       '-x' : 'unk_feature',
                       '-b' : 'input_buffer_size',
                       '-C' : 'allocate_sentence',
                       '-t' : 'theta',
                       '-c' : 'cost_factor'}

    _BOOLEAN_OPTIONS = ["all-morphs", "partial", "marginal",
                        "allocate-sentence"]

    _NBEST_MAX = 512

    _WARN_LATTICE_LEVEL = "lattice-level is DEPRECATED, " + \
                          "please use marginal or nbest"

    def __parse_mecab_options(self, enc, options):
        """Parses the MeCab options, returning them in a dictionary.

        Lattice-level option has been deprecated; please use marginal or nbest
        instead.

        Args:
            options: string or dictionary of options to use when instantiating
                the MeCab instance. May be in short- or long-form, or in a
                Python dictionary.

        Returns:
            A dictionary of the specified MeCab options, where the keys are
            snake-cased names of the long-form of the option names.

        Raises:
            MeCabError: An invalid value for N-best was passed in.
        """
        class MeCabArgumentParser(argparse.ArgumentParser):
            """MeCab option parser for natto-py."""

            def error(self, message):
                """error(message: string)

                Raises ValueError.
                """
                raise ValueError(message)

        options = options or {}
        dopts = {}

        if type(options) is dict:
            for name in iter(list(MeCab._SUPPORTED_OPTS.values())):
                if name in options:
                    if options[name]:
                        val = options[name]
                        if isinstance(val, str):
                            # <<< TODO
                            val = options[name].encode(enc)
                        dopts[name] = val
        else:
            p = MeCabArgumentParser()
            p.add_argument('-d', '--dicdir',
                           help="set DIR as a system dicdir",
                           action="store", dest="dicdir")
            p.add_argument('-u', '--userdic',
                           help="use FILE as a user dictionary",
                           action="store", dest="userdic")
            p.add_argument('-l', '--lattice-level',
                           help="lattice information level (DEPRECATED)",
                           action="store", dest='lattice_level', type=int)
            p.add_argument('-O', '--output-format-type',
                           help="set output format type (wakati, none,...)",
                           action="store", dest="output_format_type")
            p.add_argument('-a', '--all-morphs',
                           help="output all morphs (default false)",
                           action="store_true", default=False)
            p.add_argument('-N', '--nbest',
                           help="output N best results (default 1)",
                           action="store", dest='nbest', type=int)
            p.add_argument('-p', '--partial',
                           help="partial parsing mode (default false)",
                           action="store_true", default=False)
            p.add_argument('-m', '--marginal',
                           help="output marginal probability (default false)",
                           action="store_true", default=False)
            p.add_argument('-M', '--max-grouping-size',
                           help="maximum grouping size for unknown words " + \
                                "(default 24)",
                           action="store", dest='max_grouping_size', type=int)
            p.add_argument('-F', '--node-format',
                           help="use STR as the user-defined node format",
                           action="store", dest="node_format")
            p.add_argument('-U', '--unk-format',
                           help="use STR as the user-defined unknown " + \
                           "node format",
                           action="store", dest="unk_format")
            p.add_argument('-B', '--bos-format',
                           help="use STR as the user-defined " + \
                           "beginning-of-sentence format",
                           action="store", dest="bos_format")
            p.add_argument('-E', '--eos-format',
                           help="use STR as the user-defined " + \
                                "end-of-sentence format",
                           action="store", dest="eos_format")
            p.add_argument('-S', '--eon-format',
                           help="use STR as the user-defined end-of-NBest " + \
                           "format",
                           action="store", dest="eon_format")
            p.add_argument('-x', '--unk-feature',
                           help="use STR as the feature for unknown word",
                           action="store", dest="unk_feature")
            p.add_argument('-b', '--input-buffer-size',
                           help="set input buffer size (default 8192)",
                           action="store", dest='input_buffer_size', type=int)
            p.add_argument('-C', '--allocate-sentence',
                           help="allocate new memory for input sentence",
                           action="store_true", dest="allocate_sentence",
                           default=False)
            p.add_argument('-t', '--theta',
                           help="set temperature parameter theta " + \
                           "(default 0.75)",
                           action="store", dest='theta', type=float)
            p.add_argument('-c', '--cost-factor',
                           help="set cost factor (default 700)",
                           action="store", dest='cost_factor', type=int)

            opts = p.parse_args(options.split())

            for name in iter(list(MeCab._SUPPORTED_OPTS.values())):
                if hasattr(opts, name):
                    v = getattr(opts, name)
                    if v:
                        dopts[name] = v

        # final checks
        if 'nbest' in dopts \
            and (dopts['nbest'] < 1 or dopts['nbest'] > MeCab._NBEST_MAX):
            raise ValueError("Invalid N value")

        # warning for lattice-level deprecation
        if 'lattice_level' in dopts:
            sys.stderr.write("WARNING: %s\n" % MeCab._WARN_LATTICE_LEVEL)

        return dopts

    def __build_options_str(self, enc, options):
        """Returns a string concatenation of the MeCab options.

        Args:
            options: dictionary of options to use when instantiating the MeCab
                instance.

        Returns:
            A string concatenation of the options used when instantiating the
            MeCab instance, in long-form.
        """
        opts = []
        for name in iter(list(MeCab._SUPPORTED_OPTS.values())):
            if name in options:
                key = name.replace("_", "-")
                if key in self._BOOLEAN_OPTIONS:
                    if options[name]:
                        opts.append("--%s" % key)
                else:
                    opts.append("--%s=%s" % (key, options[name]))

        return " ".join(opts).encode(enc)


    def __init__(self, options=None):
        """Initializes the MeCab instance with the given options.

        Args:
            options: Optional string or dictionary of the MeCab options to be
                     used.

        Raises:
            SystemExit: An unrecognized option was passed in.
            MeCabError: An error occurred in locating the MeCab library;
                        or the FFI handle to MeCab could not be created.
        """
        try:
            env = MeCabEnv()

            # Instantiate ffi handle
            self.ffi = _ffi_libmecab()

            # Set up mecab pointer
            self.mecab = self.ffi.dlopen(env.libpath)

            # Set up byte/Unicode converters (Python 3 support)
            self.__u, self.__b = self.__string_support(env.charset)

            # Set up dictionary of MeCab options to use
            self.options = self.__parse_mecab_options(env.charset, options)

            # Set up tagger pointer
            ostr = self.__build_options_str(env.charset, self.options)
            self.tagger = self.mecab.mecab_new2(ostr)

            if self.tagger == self.ffi.NULL:
                raise MeCabError(self._ERROR_NULLPTR)
        except EnvironmentError as err:
            raise MeCabError(err)
        except ValueError as verr:
            raise MeCabError(self._ERROR_INIT % str(verr))

        # Set add'l MeCab options on the tagger as needed
        if 'partial' in self.options:
            self.mecab.mecab_set_partial(self.tagger,
                                         self.options['partial'])
        if 'theta' in self.options:
            self.mecab.mecab_set_theta(self.tagger, self.options['theta'])
        if 'lattice_level' in self.options:
            self.mecab.mecab_set_lattice_level(self.tagger,
                                               self.options['lattice_level'])
        if 'all_morphs' in self.options:
            self.mecab.mecab_set_all_morphs(self.tagger,
                                            self.options['all_morphs'])
                                            
        if 'output_format_type' in self.options or \
                'node_format' in self.options:
            self.format_node_feature = True   
        else:
            self.format_node_feature = False                                 

        # Set parsing routines for both parsing as strings and nodes
        # for both N-best and non-N-best
        if 'nbest' in self.options and self.options['nbest'] > 1:
            # N-best parsing requires lattice-level to be set
            if 'lattice_level' in self.options:
                lat = self.options['lattice_level']
            else:
                lat = 1
            self.mecab.mecab_set_lattice_level(self.tagger, lat)

            self.__parse_tostr = \
                    self.__build_parse_tostr(self._FN_NBEST_TOSTR)
            self.__parse_tonodes = \
                    self.__build_parse_tonodes(self._FN_NBEST_TONODE)
        else:
            self.__parse_tostr = \
                    self.__build_parse_tostr(self._FN_TOSTR)
            self.__parse_tonodes = \
                    self.__build_parse_tonodes(self._FN_TONODE)

        # Prepare copy for list of MeCab dictionaries
        self.dicts = []
        dptr = self.mecab.mecab_dictionary_info(self.tagger)
        while dptr != self.ffi.NULL:
            fname = self.__u(self.ffi.string(dptr.filename))
            chset = self.__u(self.ffi.string(dptr.charset))
            self.dicts.append(DictionaryInfo(dptr, fname, chset))
            dptr = getattr(dptr, 'next')

        # Save value for MeCab's internal character encoding
        self.__enc = self.dicts[0].charset

        # Set MeCab version string
        self.version = self.__u(self.ffi.string(self.mecab.mecab_version()))

    def __string_support(self, enc):
        """Returns a tuple of functions for coding/decoding bytes and Unicode.
        """
        if sys.version < '3':
            def _u(b):
                """Identity function, returns the argument string (bytes)."""
                return b
            def _b(u):
                """Identity function, returns the argument string (bytes)."""
                return u
        else:
            def _u(b):
                """Transforms byte string into Unicode."""
                return b.decode(enc)
            def _b(u):
                """Transforms Unicode string into encoded bytes."""
                return u.encode(enc)
        return(_u, _b)

    def __build_parse_tostr(self, fn_name):
        """Builds and returns the MeCab function for parsing Unicode text.

        Args:
            fn_name: MeCab function name that determines the function
                behavior, either 'mecab_sparse_tostr' or
                'mecab_nbest_sparse_tostr'.

        Returns:
            A function definition, tailored to parsing Unicode text and
            returning the result as a string suitable for display on stdout,
            using either the default or N-best behavior.
        """
        def _fn(text):
            """Parse text and return MeCab result as string."""
            args = [self.tagger]
            if fn_name == self._FN_NBEST_TOSTR:
                args.append(self.options['nbest'])
            args.append(text)

            res = getattr(self.mecab, fn_name)(*args)
            if res != self.ffi.NULL:
                raw = self.ffi.string(res)
                return self.__u(raw).strip()
            else:
                err = self.mecab.mecab_strerror((self.tagger))
                raise MeCabError(self.__u(self.ffi.string(err)))
        return _fn

    def __build_parse_tonodes(self, fn_name):
        """Builds and returns the MeCab function for parsing to nodes.

        Args:
            fn_name: MeCab function name that determines the function
                behavior, either 'mecab_sparse_tonode' or 'mecab_nbest_init'.

        Returns:
            A function definition, tailored to parsing as nodes, using either
            the default or N-best behavior.
        """
        def _fn(text):
            """Parse text and return MeCab result as a node."""

            if fn_name == self._FN_NBEST_TONODE:
                # N-best node parsing
                getattr(self.mecab, fn_name)(self.tagger, text)
                nptr = self.mecab.mecab_nbest_next_tonode(self.tagger)
                count = self.options['nbest']
            else:
                # default string-based node parsing
                nptr = getattr(self.mecab, fn_name)(self.tagger, text)
                count = 1

            nodes = []
            if nptr != self.ffi.NULL:
                for _ in range(count):
                    while nptr != self.ffi.NULL:
                        # ignore any BOS nodes?
                        if nptr.stat != MeCabNode.BOS_NODE:
                            raws = self.ffi.string(nptr.surface[0:nptr.length])
                            surf = self.__u(raws).strip()
                            
                            if self.format_node_feature:
                                rawf = self.ffi.string(self.mecab.mecab_format_node(self.tagger, nptr))
                            else:
                                rawf = self.ffi.string(nptr.feature)
                            feat = self.__u(rawf).strip()

                            mnode = MeCabNode(nptr, surf, feat)
                            nodes.append(mnode)
                        nptr = getattr(nptr, 'next')

                    if fn_name == self._FN_NBEST_TONODE:
                        nptr = self.mecab.mecab_nbest_next_tonode(self.tagger)
                return nodes
            else:
                err = self.mecab.mecab_strerror((self.tagger))
                raise MeCabError(self.__u(self.ffi.string(err)))
        return _fn

    def __repr__(self):
        """Returns a string representation of this MeCab instance."""
        return self._REPR_FMT % (type(self).__module__,
                                 type(self).__name__,
                                 self.tagger,
                                 self.options,
                                 self.dicts,
                                 self.version)

    def parse(self, text, as_nodes=False):
        """Parses the given Unicode text.

        Args:
            text: the text to parse.
            as_nodes: flag indicating whether to parse as nodes or strings;
                defaults to False (string parsing).

        Raises:
            MeCabError: a null argument was passed in;
                        or an unforseen error occurred during the operation.
        """
        if text is None:
            raise MeCabError(self._ERROR_EMPTY_STR)

        btext = self.__b(text)
        if as_nodes:
            return self.__parse_tonodes(btext)
        else:
            return self.__parse_tostr(btext)

class DictionaryInfo(object):
    """Representation of a MeCab dictionary, wrapping mecab_dictionary_info_t.

    A list of dictionaries used by MeCab is returned by the dicts attribute of
    MeCab. Each dictionary information includes the attributes listed below.

    Attributes:
        ptr: This dictionary's pointer.
        filename: Full path to the dictionary file.
        charset: Dictionary character set, e.g., "SHIFT-JIS", "UTF-8".
        size: Number of words registered in this dictionary.
        type: Dictionary type; 0 (SYS_DIC), 1 (USR_DIC), 2 (UNK_DIC)
        lsize: Left attributes size.
        rsize: Right attributes size.
        version: Dictionary version.
        next: Pointer to next dictionary information struct.

    Example usage:

        import natto

        nm = natto.MeCab()

        sysdic = nm.dicts[0]

        print sysdic.filename

        print sysdic.charset

        print sysdic.is_sysdic()
    """

    _REPR_FMT = '<%s.%s pointer=%s, type="%d", filename="%s", charset="%s">'

    # System dictionary
    SYS_DIC = 0
    # User dictionary.
    USR_DIC = 1
    # Unknown dictionary.
    UNK_DIC = 2

    def __init__(self, dptr, filename, charset):
        """Initializes the MeCab dictionary information."""
        self.ptr = dptr
        self.filename = filename
        self.charset = charset
        self.size = dptr.size
        self.type = dptr.type
        self.lsize = dptr.lsize
        self.rsize = dptr.rsize
        self.version = dptr.version
        self.next = getattr(dptr, 'next')

    def is_sysdic(self):
        """Returns True if this is a system dictionary."""
        return self.type == self.SYS_DIC

    def is_usrdic(self):
        """Returns True if this is a user-defined dictionary."""
        return self.type == self.USR_DIC

    def is_unkdic(self):
        """Returns True if this is a unknown dictionary."""
        return self.type == self.UNK_DIC

    def __repr__(self):
        """Returns a string representation of this MeCab dictionary."""
        return self._REPR_FMT % (type(self).__module__,
                                 type(self).__name__,
                                 self.ptr,
                                 self.type,
                                 self.filename,
                                 self.charset)


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


class MeCabError(Exception):
    """MeCabError is a general error class for the natto-py package."""


"""
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
"""
