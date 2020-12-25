#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Find name patterns in a tree"""

import KmdCmd
import KmdFiles

import os, sys, re, time
import logging

class KmdFindPatterns(KmdCmd.KmdCommand):
    def extendParser(self):
        super(KmdFindPatterns, self).extendParser()
        #Extend parser
        self.parser.add_argument('srctree', metavar='</path/to/srctree>', nargs=1, help='Root of a src tree')

    def run(self):
     
        #patterns = {} #store patterns and matching file names
        knownpatterns = [
            r'^(\d\d\d\d)(\d\d)(\d\d)_.*?$',
            ]
                
        for root, _, files in os.walk(self.args.srctree[0]):
            for name in files:
                #for each file in the folder
                p = os.path.join(root, name)
                m = None
                for k in knownpatterns :
                    m = re.compile(k, re.I).match(name)
                    if m :
                      break
                if not m :
                    logging.debug("not matching file : %s", p)    
                    continue
                logging.debug("Groups %s", m.groups())
                logging.debug("Matching file : %s", p)
                olddt = KmdFiles.get_modification_date(p)
                logging.debug("OLDDT : %s", olddt)
                newdt = olddt.replace(
                  year = int(m.groups()[0]),
                  month = int(m.groups()[1]),
                  day = int(m.groups()[2])
                  )
                logging.debug("NEWDT : %s", newdt)
                ts = time.mktime(newdt.timetuple())
                
                logging.debug("TS : %s", ts)
                logging.info("Changing time for %s to %s", p, ts)
                if self.args.doit :
                      KmdFiles.set_modification_date(p, ts)

if __name__ == "__main__":
    cmd = KmdFindPatterns(__doc__)
    cmd.run()

