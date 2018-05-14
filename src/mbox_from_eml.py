#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parse tree, find EML files, and move them info a new mbox"""

import KmdCmd
import KmdFiles
import KmdMbox
import os
import re
import logging
import mailbox
import email

class KmdFilesMove(KmdCmd.KmdCommand):
    def extendParser(self):
        super(KmdFilesMove, self).extendParser()
        #Extend parser
        self.parser.add_argument('tree', metavar='</path/to/tree>', nargs=1, help='The source tree')
        self.parser.add_argument('mbox', metavar='</path/to/dest>', nargs=1, help='Mbox File to store eml')
        
    def run(self):
        mboxpath = self.args.mbox[0]
        doit = self.args.doit :
    
        if not os.path.isfile(mboxpath) :
            logging.info("Create new MBOX in %s, mbopath)
        if doit :
            tombox = mailbox.mbox(mboxpath)

        c = 0
        
        logging.info("Parsing %s", self.args.tree[0])
        for root, dirs, files in os.walk(self.args.tree[0]):
            logging.debug("Walking in %s", root)
            for name in files:
                pname = os.path.join(root, name)
                try :
                    fp = open(pname, 'r')
                    msg = email.message_from_file(fp)
                    fp.close()
                except :
                    continue
                c += 1                
                if doit :
                    KmdMbox.messageAddToMbox(tombox, msg)

        logging.info("%d Messages imported", c)

if __name__ == "__main__":
    cmd = KmdFilesMove(__doc__)
    cmd.run()
