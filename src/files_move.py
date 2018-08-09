#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parse tree, find matching files (with name or mime type), and move them info a new folder"""

import KmdCmd
import KmdFiles
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
        self.parser.add_argument(
            'regexp', metavar='<regexp>', nargs=1, help='Perl regexp matching files')
        self.parser.add_argument(
            'folder', metavar='</path/to/dest>', nargs=1, help='Folder to put matching files')
        self.parser.add_argument(
            '--mime', action="store_true", help='Filter with mime type')

    def run(self):
        self.regexp = re.compile(self.args.regexp[0])
        if self.args.mime:
            logging.debug("Loading Magic python module")
            import magic
            mime = magic.open(magic.MIME_TYPE)
            mime.load()

        logging.info("Parsing %s", self.args.tree[0])
        for root, dirs, files in os.walk(self.args.tree[0]):
            logging.debug("Walking in %s", root)
            for name in files:

                if self.args.mime:
                    try:
                        pname = os.path.join(root, name)
                        matchname = mime.file(pname)
                        logging.debug("Mime %s for %s" % (matchname, pname))
                    except:
                        logging.debug(
                            "Exception when check mimetype of %s" % pname)
                        matchname = "None/Exception"
                else:
                    matchname = name

                if self.regexp.match(matchname):
                    logging.debug("Found %s", name)
                    pname = os.path.join(root, name)
                    dname = os.path.join(self.args.folder[0], name)
                    KmdFiles.fileMoveRename(pname, dname, self.args.doit)


if __name__ == "__main__":
    cmd = KmdFilesMove(__doc__)
    cmd.run()
