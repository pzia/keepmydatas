#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Remove empty dirs in the provided trees"""

import KmdCmd
import KmdFiles
import logging


class KmdTreeEmptyDirs(KmdCmd.KmdCommand):
    def extendParser(self):
        """extend parser"""
        super(KmdTreeEmptyDirs, self).extendParser()
        # Extend parser
        self.parser.add_argument('folders', metavar='</path/to/tree>',
                                 nargs="+", help='the list of file trees to clean-up')

    def run(self):
        """Run the clean-up"""
        for folder in self.args.folders:
            # FIXME : Test if folder exists ?
            logging.info("Traverse %s", folder)
            KmdFiles.removeEmptyFolders(folder, self.args.doit)


if __name__ == "__main__":
    KmdTreeEmptyDirs(__doc__).run()
