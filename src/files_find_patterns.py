#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Find name patterns in a tree"""

import KmdCmd
import KmdFiles

import os, sys, re
import logging

class KmdFindPatterns(KmdCmd.KmdCommand):
    def extendParser(self):
        super(KmdFindPatterns, self).extendParser()
        #Extend parser
        self.parser.add_argument('srctree', metavar='</path/to/srctree>', nargs=1, help='Root of a src tree')

    def run(self):
     
        patterns = {} #store patterns and matching file names
        knownpatterns = [
            r'\w*(\d\d\d\d)(\d\d)(\d\d)[_t]\d\d\d\d\d.*?\.jpg',
            r'(\d\d\d\d)-(\d\d)-(\d\d) \d\d\.\d\d\.\d\d.*?\.jpg',
            r'img(\d\d)(\d\d)(\d\d)-\d\d\d\d.*?\.jpg',
            ]
        
        rechar = re.compile(r'\w')
        reint = re.compile(r'\d')
        
        for root, dirs, files in os.walk(self.args.srctree[0]):
            for name in files:
                known = False
                for k in knownpatterns :
                    if re.compile(k, re.I).match(name):
                        known = True
                        continue
                if known :
                    continue

                #for each file in the folder
                p = os.path.join(root, name)

                pat = r""
                for c in range(0, len(name)):
                    if reint.match(name[c]):
                        pat += '\d'
                    else : 
                        pat += name[c].lower()
                if pat not in patterns :
                    patterns[pat] = []
                patterns[pat].append(p)

        def sbylen(k):
            return len(patterns[k])
        sp = sorted(patterns, key=sbylen, reverse=True)
        patterns2 = {}

        for p in sp :
            if len(patterns[p]) < 2:
                continue
            if p.count(r'\d') < 6 :
                continue 
            print("%d = %s " % (len(patterns[p]), p), patterns[p][0])

if __name__ == "__main__":
    cmd = KmdFindPatterns(__doc__)
    cmd.run()

