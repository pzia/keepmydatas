#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parse tree and find files matching owncloud conflict file pattern.
If the conflict file has the same sha256 as the initial file, remove it.
"""

import KmdCmd
import KmdFiles
import os
import re
import logging


class KmdOwncloudDedup(KmdCmd.KmdCommand):
    regexp = r'^(.*)(_conflict-\d{8}-\d{6})(.*)$'

    def extendParser(self):
        super(KmdOwncloudDedup, self).extendParser()
        # Extend parser
        self.parser.add_argument(
            'folders', metavar='</path/to/tree>', nargs='+', help='The source tree')
        self.parser.add_argument('--moveto', metavar='</path/to/folder>', nargs=1,
                                 default=None, help='Path to move orphans (else they are renamed in place)')
        self.parser.add_argument(
            '--forcedelete', action="store_true", help='Force removal of Owncloud conflict files')

    def run(self):
        owncloudre = re.compile(self.regexp)

        for folder in self.args.folders:
            logging.info("Running in %s", folder)
            for root, dirs, files in os.walk(folder):
                for i in files:
                    m = owncloudre.match(i)
                    if m != None:
                        parts = m.groups()
                        origname = "%s%s" % (parts[0], parts[2])
                        origpath = os.path.join(root, origname)
                        curpath = os.path.join(root, i)
                        if not os.path.exists(origpath):
                            logging.debug(
                                "%s doesn't exist anymore" % origpath)
                            if self.args.moveto != None:
                                origpath = os.path.join(
                                    self.args.move_orphans, origname)
                            logging.info("Restoring file to %s", origpath)
                            if self.args.doit:
                                KmdFiles.fileMoveRename(
                                    curpath, origpath, self.args.doit)
                        elif KmdFiles.fileSHA(origpath) == KmdFiles.fileSHA(curpath):
                            logging.info("Removing %s", curpath)
                            if self.args.doit:
                                os.remove(curpath)
                        elif self.args.forcedelete:
                            logging.info("Force Delete %s", curpath)
                            if self.args.doit:
                                os.remove(curpath)
                        else:
                            logging.warn("Keeping %s != %s", origpath, curpath)


if __name__ == "__main__":
    cmd = KmdOwncloudDedup(__doc__)
    cmd.run()
