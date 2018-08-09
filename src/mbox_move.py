#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parse tree, find matching MBOX files, and move them info a new folder"""

import KmdCmd
import KmdFiles
import KmdMbox
import os
import re
import logging


class KmdFilesMove(KmdCmd.KmdCommand):
    regexp = None

    def extendParser(self):
        super(KmdFilesMove, self).extendParser()
        # Extend parser
        self.parser.add_argument(
            'tree', metavar='</path/to/tree>', nargs=1, help='The source tree')
        self.parser.add_argument('regexp', metavar='<regexp>', default='.*(thunderbird|mozilla|message|mail|evolution|mbox|imap|lotus).*',
                                 nargs=1, help='Perl regexp matching files PATH (Example : .*thundebird.*')
        self.parser.add_argument(
            'folder', metavar='</path/to/dest>', nargs=1, help='Folder to put matching files')

    def run(self):
        self.regexp = re.compile(self.args.regexp[0], re.IGNORECASE)

        logging.info("Parsing %s", self.args.tree[0])
        for root, dirs, files in os.walk(self.args.tree[0]):
            logging.debug("Walking in %s", root)
            for name in files:
                pname = os.path.join(root, name)
                if self.regexp.match(pname) and KmdMbox.isFileMbox(pname):
                    logging.debug("Found %s", name)
                    dname = os.path.join(self.args.folder[0], name)
                    KmdFiles.fileMoveRename(pname, dname, self.args.doit)


if __name__ == "__main__":
    cmd = KmdFilesMove(__doc__)
    cmd.run()
