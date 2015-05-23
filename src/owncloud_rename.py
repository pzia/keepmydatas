#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Parse tree and find files matching owncloud forbidden characters.
Rename in place or move into a specific folder
"""

import KmdCmd
import KmdFiles
import os, re
import logging

class KmdOwncloudRename(KmdCmd.KmdCommand):
    regexp = r'[\*:"?><|]+'

    def extendParser(self):
        super(KmdOwncloudRename, self).extendParser()
        #Extend parser
        self.parser.add_argument('folders', metavar='</path/to/tree>', nargs='+', help='The source tree')
        self.parser.add_argument('--moveto', metavar='</path/to/folder>', nargs=1, default=None, help='Path to move bad named files')
        
    def run(self):
        owncloudre = re.compile(self.regexp)

        for folder in self.args.folders :
            logging.info("Running in %s", folder) 
            for root, dirs, files in os.walk(folder): 
                for i in files:
                    m = owncloudre.search("%s" % i)
                    if m is not None :
                        newname = owncloudre.sub('_', i)
                        logging.info("Renaming %s into %s", i, newname)
                        if self.args.doit :
                            origpath = os.path.join(root, i)
                            newpath = os.path.join(root, newname)
                            KmdFiles.fileMoveRename(origpath, newpath, self.args.doit)
                            logging.debug("Done : %s -> %s", origpath, newpath)

if __name__ == "__main__":
    cmd = KmdOwncloudRename(__doc__)
    cmd.run()
