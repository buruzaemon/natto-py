# -*- coding: utf-8 -*-
"""MeCab option parser for natto-py."""
from __future__ import print_function
import argparse
import sys


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

_WARN_LATTICE_LEVEL = "lattice-level is DEPRECATED, " + \
                      "please use marginal or nbest"

def _parse_mecab_options(options={}):
    """Parses the MeCab options, returning them in a dictionary.

    Lattice-level option has been deprecated; please use marginal or nbest
    instead.

    Args:
        options: string or dictionary of options to use when instantiating
            the MeCab instance. May be in short- or long-form, or in a Python
            dictionary.

    Returns:
        A dictionary of the specified MeCab options, where the keys are
        snake-cased names of the long-form of the option names.

    Raises:
        MeCabError: An invalid value for N-best was passed in.
    """
    dopts = {}
    
    if type(options) is str:
        p = argparse.ArgumentParser()
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
                       help="maximum grouping size for unknown words" + \
                            "(default 24)",
                       action="store", dest='max_grouping_size', type=int)
        p.add_argument('-F', '--node-format',
                       help="use STR as the user-defined node format",
                       action="store", dest="node_format")
        p.add_argument('-U', '--unk-format',
                       help="use STR as the user-defined unknown node format",
                       action="store", dest="unk_format")
        p.add_argument('-B', '--bos-format',
                       help="use STR as the user-defined " + \
                       "beginning-of-sentence format",
                       action="store", dest="bos_format")
        p.add_argument('-E', '--eos-format',
                       help="use STR as the user-defined end-of-sentence " + \
                            "format",
                       action="store", dest="eos_format")
        p.add_argument('-S', '--eon-format',
                       help="use STR as the user-defined end-of-NBest format",
                       action="store", dest="eon_format")
        p.add_argument('-x', '--unk-feature',
                       help="use STR as the feature for unknown word",
                       action="store", dest="unk_feature")
        p.add_argument('-b', '--input-buffer-size',
                       help="set input buffer size (default 8192)",
                       action="store", dest='input_buffer_size', type=int)
        p.add_argument('-C', '--allocate-sentence',
                       help="allocate new memory for input sentence",
                       action="store_true", default=False)
        p.add_argument('-t', '--theta',
                       help="set temperature parameter theta (default 0.75)",
                       action="store", dest='theta', type=float)
        p.add_argument('-c', '--cost-factor',
                       help="set cost factor (default 700)",
                       action="store", dest='cost_factor', type=int)
        
        opts = p.parse_args(options.split())
        nomme = _SUPPORTED_OPTS.itervalues()
        for n in nomme:
            if hasattr(opts, n):
                v = getattr(opts, n)
                if v:
                    dopts[n] = v
    elif type(options) is dict:                    
        nomme = _SUPPORTED_OPTS.itervalues()
        for n in nomme:
            if options.has_key(n):
                if options[n]:
                    dopts[n] = options[n]

    # final checks
    if dopts.has_key('nbest') and (dopts['nbest'] < 1 or dopts['nbest'] > 512):
        raise ValueError("Invalid N value")

    # warning for lattice-level deprecation
    if dopts.has_key('lattice_level'):
        _warning(_WARN_LATTICE_LEVEL)

    return dopts

def _build_options_str(options):
    """Returns a string concatenation of the MeCab options.

    Args:
        options: dictionary of options to use when instantiating the MeCab
            instance.

    Returns:
        A string concatenation of the options used when instantiating the
        MeCab instance, in long-form.
    """

    opt = []
    nomme = _SUPPORTED_OPTS.itervalues()
    for n in nomme:
        if options.has_key(n):
            key = n.replace("_", "-")
            if key == "all-morphs" or key == "allocate-sentence":
                if options[n]:
                    opt.append("--%s" % key)
            else:
                opt.append("--%s=%s" % (key, options[n]))
    return " ".join(opt)

def _warning(*objs):
    """Prints a warning message to STDERR

    Args:
        objs: objects for printing to STDERR
    """
    print("WARNING: ", *objs, file=sys.stderr)


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
