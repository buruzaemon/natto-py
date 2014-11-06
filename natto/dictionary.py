# -*- coding: utf-8 -*-
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

