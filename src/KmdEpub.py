#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Epub utils."""

import logging
import os
import zipfile
from lxml import etree

mimtype = "application/epub+zip"

def isFileEpub(path, forceMime = False):
    magicline = ""
    try :
        if not os.path.exists(path):
            logging.debug("%s does not exist" % path)
            return False
        # prepare to read from the .epub file
        zf = zipfile.ZipFile(path)
        mime = zf.read('mimetype')
    
        if mime.strip() != "application/epub+zip" and not forceMime:
            return False    

        return True
    except :
        logging.debug("Something went testing epub candidate %s", path)
        return False

def metadatas(fname):
    try :
        ns = {
            'n':'urn:oasis:names:tc:opendocument:xmlns:container',
            'pkg':'http://www.idpf.org/2007/opf',
            'dc':'http://purl.org/dc/elements/1.1/'
        }

        # prepare to read from the .epub file
        zf = zipfile.ZipFile(fname)

        # find the contents metafile
        txt = zf.read('META-INF/container.xml')
        tree = etree.fromstring(txt)
        cfname = tree.xpath('n:rootfiles/n:rootfile/@full-path',namespaces=ns)[0]

        # grab the metadata block from the contents metafile
        cf = zf.read(cfname)
        tree = etree.fromstring(cf)
        px = tree.xpath('/pkg:package/pkg:metadata',namespaces=ns)
        p = px[0]

        # repackage the data
        res = {}
        for s in ['title','language','creator','date','identifier']:
            try :
                r = p.xpath('dc:%s/text()'%(s),namespaces=ns)
                v = r[0]
            except :  
                v = "Unknown"
            res[s] = v.strip()
        return res
    except :
        return None

def metadata(epub, name, default = "Unknown") :
    import ebooklib.epub
    try :
        d = epub.get_metadata('DC', name)[0][0].strip()
        return d
    except :
        return default
