#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Parse tree and find duplicates files.
Delete duplicates if they are near enough (default is : same dir)
"""

import KmdCmd
import KmdFiles
import os
import logging

class KmdFilesDedup(KmdCmd.KmdCommand):
    regexp = None
    def extendParser(self):
        super(KmdFilesDedup, self).extendParser()
        #Extend parser
        self.parser.add_argument('tree', metavar='</path/to/tree>', nargs='+', help='The source tree')
        #FIXME : --distance not working for now
        #self.parser.add_argument('--distance', metavar='<integer>', default=0, help='Maximum distance in the tree allowed to delete duplicates')
        self.parser.add_argument('--samedir', action="store_true", help='Delete all duplicates if all are in the same dir')
        self.parser.add_argument('--trashtree', metavar='</path/to/tree>', nargs='+', help="Delete all duplicates in one of the trashtree")
        
    def run(self):
        shaf = KmdFiles.treeDetectDoubles(self.args.tree)
        if self.args.samedir :
            self.run_samedir(shaf)
        elif self.args.trashtree :
            self.run_trashtree(shaf)
        else :
            self.run_samedir(shaf)

    def run_trashtree(self, shaf):
        for listoffiles in shaf.values():
#            print(listoffiles)
            pathlist = []
            c = len(listoffiles)
            for f in listoffiles :
                p = os.path.dirname(f)
                for t in self.args.trashtree :
                    if t in p :
                        c -= 1
                        pathlist.append(f)
                        break
            if c and len(pathlist):
                #print(listoffiles)
                for f in pathlist :
                    logging.info("Removing duplicate %s", f)
                    if self.args.doit :
                        os.remove(f)
        
    def run_samedir(self, shaf):
        for listoffiles in shaf.values():
            pathlist = []
            for f in listoffiles :
                p = os.path.dirname(f)
                #FIXME : here we should do some magic to test the distance
                if p not in pathlist :
                    pathlist.append(p)
            if len(pathlist) == 1 :
                #FIXME : here we should try to compute a "good" name for the main file (maybe the longest name in common ?)
                for f in listoffiles[1:]:
                    logging.info("Removing duplicate %s", f)
                    if self.args.doit :
                        os.remove(f)

if __name__ == "__main__":
    KmdFilesDedup(__doc__).run()
