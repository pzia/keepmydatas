#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Parse source tree, get old files and move files info a new folder tree"""

import KmdCmd
import KmdFiles
import os
import re
import logging

class KmdFilesMove(KmdCmd.KmdCommand):
    regexp = None
    def extendParser(self):
        super(KmdFilesMove, self).extendParser()
        #Extend parser
        self.parser.add_argument('source', metavar='</path/to/tree>', nargs=1, help='The source tree')
        self.parser.add_argument('tree', metavar='</path/to/dest>', nargs=1, help='Folder to put matching files')
        self.parser.add_argument('age', metavar='<days>', nargs=1, help='age')

        
    def run(self):
        logging.info("Parsing %s", self.args.source[0])
        for root, _, files in os.walk(self.args.source[0]):
            logging.debug("Walking in %s", root)
            for name in files:
                pname = os.path.join(root, name)
                dname = os.path.join(self.args.tree[0])
                try :
                    KmdFiles.fileMoveRenameToDirIfOld(pname, dname, int(self.args.age[0]), self.args.doit)
                except :
                    logging.error("Bad move from %s to %s", pname, dname)
        KmdFiles.removeEmptyFolders(self.args.source[0], self.args.doit)
                
if __name__ == "__main__":
    cmd = KmdFilesMove(__doc__)
    cmd.run()
