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

    def run(self):
        for folder in cmd.args.folders :
            KmdImages.cleanDir(folder, cmd.args.doit)

if __name__ == "__main__":
    cmd = KmdImagesMerge(__doc__)
    cmd.run()

