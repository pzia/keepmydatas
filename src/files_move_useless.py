#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parse tree, find useless files (with name pattern) and remove them
"""

import KmdCmd
import KmdFiles
import os
import re
import logging

class KmdFilesMove(KmdCmd.KmdCommand):
    regexp = []
    
    def extendParser(self):
        super(KmdFilesMove, self).extendParser()
        #Extend parser
        self.parser.add_argument('tree', metavar='</path/to/tree>', nargs=1, help='The source tree')
        self.parser.add_argument('folder', metavar='</path/to/dest>', nargs=1, help='Folder to put useless files')
        self.parser.add_argument('--list', action="store_true", help='List match pattern')

    def match2regexp(self, match):
        r = match.rstrip()
        if len(r) == 0 :
            return None
        #backup special characters
        r = r.replace(".", "[DOT]")
        r = r.replace("$", "[DOLLARS]")
        if r[0] == "]":
            r = r[1:]
        r = "^" + r


        #convert to regexp
        r = r.replace("*", ".*")
        r = r.replace("?", ".?")
        #restore special characters
        r = r.replace("[DOT]", "\.")
        r = r.replace("[DOLLARS]", "\$")
        
        r = r+"$"
        return r
    
    def populateRegexp(self, filepath):
        f = open(filepath, 'r')
        for line in f.readlines():
            regline = self.match2regexp(line)
            if regline == None :
                continue
            logging.debug("Useless pattern : %s " % regline)
            self.regexp.append(re.compile(regline))
        f.close()
        
    def run(self):
        self.populateRegexp("useless.lst")

        if self.args.list:
            for r in self.regexp :
                print(r.pattern)
            return

        logging.info("Parsing %s", self.args.tree[0])
        for root, dirs, files in os.walk(self.args.tree[0]):
            logging.debug("Walking in %s", root)
            for name in files:
                pname = os.path.join(root, name)
                logging.debug("Testing %s" % pname)
                for r in self.regexp:
                    if r.match(name):
                        logging.debug("Found %s with %s", pname, r.pattern)
                        dname = os.path.join(self.args.folder[0], name)
                        KmdFiles.fileMoveRename(pname, dname, self.args.doit)
                        break

if __name__ == "__main__":
    cmd = KmdFilesMove(__doc__)
    cmd.run()
