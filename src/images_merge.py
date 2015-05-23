#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Recursively detect same images and try to merge metadatas before deleting duplicates"""

import KmdImages
import KmdCmd

class KmdImagesMerge(KmdCmd.KmdCommand):
    def extendParser(self):
        super(KmdImagesMerge, self).extendParser()
        #Extend parser
        self.parser.add_argument('folders', metavar='</path/to/folder>', nargs='+', help='A list of folders')
        self.parser.add_argument('--quick', action="store_true", help='Compare only if size differs for more than 1000 bytes')

    def run(self):
        for folder in cmd.args.folders :
            KmdImages.cleanDir(folder, cmd.args.doit, quick = cmd.args.quick)

if __name__ == "__main__":
    cmd = KmdImagesMerge(__doc__)
    cmd.run()

