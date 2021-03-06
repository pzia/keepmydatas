#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Parse tree, find matching files (with name or mime type), and move them info a new folder"""

import KmdCmd
import KmdFiles
import KmdEpub
import os
import logging

class KmdEpubRename(KmdCmd.KmdCommand):
    regexp = None
    def extendParser(self):
        super(KmdEpubRename, self).extendParser()
        #Extend parser
        self.parser.add_argument('tree', metavar='</path/to/tree>', nargs=1, help='The source tree')
        self.parser.add_argument('folder', metavar='</path/to/dest>', nargs=1, help='Folder to put matching files')
        
    def run(self):
        logging.info("Parsing %s", self.args.tree[0])
        for root, _, files in os.walk(self.args.tree[0]):
            logging.debug("Walking in %s", root)
            for name in files:
                pname = os.path.join(root, name)
                if KmdEpub.isFileEpub(pname):
                    logging.info("Found %s", name)
                    metadatas = KmdEpub.metadatas(pname)
                    dirname = os.path.join(self.args.folder[0], metadatas['creator'])
                    if not os.path.exists(dirname) :
                        #new tree
                        if self.args.doit :
                            os.makedirs(dirname)
                    dname = os.path.join(self.args.folder[0], metadatas['creator'], metadatas['title']+".epub")
                    KmdFiles.fileMoveRename(pname, dname, self.args.doit)

if __name__ == "__main__":
    cmd = KmdEpubRename(__doc__)
    cmd.run()
