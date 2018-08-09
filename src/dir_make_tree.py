#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parse dir, split files into aa/bb/ tree"""

import KmdCmd
import KmdFiles
import os
import re
import logging


class KmdDirMakeTree(KmdCmd.KmdCommand):
    regexp = None

    def extendParser(self):
        super(KmdDirMakeTree, self).extendParser()
        # Extend parser
        self.parser.add_argument(
            'folder', metavar='</path/to/folder>', nargs=1, help='The source folder')

    def run(self):
        logging.info("Parsing %s", self.args.folder[0])
        for root, dirs, files in os.walk(self.args.folder[0]):
            logging.debug("Walking in %s", root)
            for name in files:
                lowname = name.lower()
                p1 = lowname[0:2]
                p2 = lowname[2:4]
                p3 = lowname[4:6]
                pname = os.path.join(root, name)
                dest = os.path.join(self.args.folder[0], p1, p2, p3)
                if not os.path.exists(dest) and self.args.doit:
                    os.makedirs(dest)
                KmdFiles.fileMoveRenameToDir(pname, dest, self.args.doit)


if __name__ == "__main__":
    cmd = KmdDirMakeTree(__doc__)
    cmd.run()
