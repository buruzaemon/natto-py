# -*- coding: utf-8 -*-
'''Binding via CFFI to the MeCab library.'''
import cffi

def _ffi_libmecab():
    '''Returns an FFI interface to MeCab library.

    Library definition is from mecab.h.
    '''
    ffi = cffi.FFI()
    ffi.cdef('''
        struct mecab_dictionary_info_t {
            const char                        *filename;
            const char                        *charset;
            unsigned int                       size;
            int                                type;
            unsigned int                       lsize;
            unsigned int                       rsize;
            unsigned short                     version;
            struct mecab_dictionary_info_t    *next;
        };

        struct mecab_path_t {
            struct mecab_node_t*               rnode;
            struct mecab_path_t*               rnext;
            struct mecab_node_t*               lnode;
            struct mecab_path_t*               lnext;
            int                                cost;
            float                              prob;
        };

        struct mecab_node_t {
            struct mecab_node_t               *prev;
            struct mecab_node_t               *next;
            struct mecab_node_t               *enext;
            struct mecab_node_t               *bnext;
            struct mecab_path_t               *rpath;
            struct mecab_path_t               *lpath;
            const char                        *surface;
            const char                        *feature;
            unsigned int                       id;
            unsigned short                     length;
            unsigned short                     rlength;
            unsigned short                     rcAttr;
            unsigned short                     lcAttr;
            unsigned short                     posid;
            unsigned char                      char_type;
            unsigned char                      stat;
            unsigned char                      isbest;
            float                              alpha;
            float                              beta;
            float                              prob;
            short                              wcost;
            long                               cost;
        };

        typedef struct   mecab_t                 mecab_t;
        typedef struct   mecab_model_t           mecab_model_t;
        typedef struct   mecab_lattice_t         mecab_lattice_t;
        typedef struct   mecab_dictionary_info_t mecab_dictionary_info_t;
        typedef struct   mecab_node_t            mecab_node_t;
        typedef struct   mecab_path_t            mecab_path_t;

        // Model interface
        mecab_model_t   *mecab_model_new2(const char *arg);
        void             mecab_model_destroy(mecab_model_t *model);
        mecab_t         *mecab_model_new_tagger(mecab_model_t *model);
        mecab_lattice_t *mecab_model_new_lattice(mecab_model_t *model);
        const mecab_dictionary_info_t* mecab_model_dictionary_info(mecab_model_t *model);

        // old Tagger interface
        void             mecab_destroy(mecab_t *mecab);
        const char*      mecab_version();
        const char*      mecab_strerror(mecab_t *mecab);
        const char*      mecab_format_node(mecab_t *mecab, const mecab_node_t *node);

        // Lattice interface
        void             mecab_lattice_destroy(mecab_lattice_t *lattice);
        void             mecab_lattice_clear(mecab_lattice_t *lattice);
        int              mecab_lattice_is_available(mecab_lattice_t *lattice);
        const char      *mecab_lattice_strerror(mecab_lattice_t *lattice);

        const char      *mecab_lattice_get_sentence(mecab_lattice_t *lattice);
        void             mecab_lattice_set_sentence(mecab_lattice_t *lattice, const char *sentence);
        size_t           mecab_lattice_get_size(mecab_lattice_t *lattice);
        void             mecab_lattice_set_theta(mecab_lattice_t *lattice, double theta);
        void             mecab_lattice_set_z(mecab_lattice_t *lattice, double Z);
        int              mecab_lattice_get_request_type(mecab_lattice_t *lattice);
        void             mecab_lattice_add_request_type(mecab_lattice_t *lattice, int request_type);
        void             mecab_lattice_set_request_type(mecab_lattice_t *lattice, int request_type);
        int              mecab_lattice_get_boundary_constraint(mecab_lattice_t *lattice, size_t pos);
        void             mecab_lattice_set_boundary_constraint(mecab_lattice_t *lattice, size_t pos, int boundary_type);
        const char      *mecab_lattice_get_feature_constraint(mecab_lattice_t *lattice, size_t pos);
        void             mecab_lattice_set_feature_constraint(mecab_lattice_t *lattice, size_t begin_pos, size_t end_pos, const char *feature);

        int              mecab_parse_lattice(mecab_t *mecab, mecab_lattice_t *lattice);
        int              mecab_lattice_next(mecab_lattice_t *lattice);
        const char      *mecab_lattice_tostr(mecab_lattice_t *lattice);
        const char      *mecab_lattice_nbest_tostr(mecab_lattice_t *lattice, size_t N);
        mecab_node_t    *mecab_lattice_get_bos_node(mecab_lattice_t *lattice);
    ''')
    return ffi

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
