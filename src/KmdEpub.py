#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Epub utils."""

import logging
import os
import ebooklib.epub

mimtype = "application/epub+zip"

def isFileEpub(path):
    magicline = ""
    try :
        if not os.path.exists(path):
            logging.debug("%s does not exist" % path)
            return False
        r = ebooklib.epub.read_epub(path)
        return True
    except :
        logging.debug("Something went testing epub candidate %s", path)
        return False
        
def metadata(epub, name, default = "Unknown") :
    try :
        d = epub.get_metadata('DC', name)[0][0]
        return d
    except :
        return default
