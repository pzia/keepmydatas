#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compare all messages within a tree with those stored in a date tree (yyyy/mm)"""

import KmdMbox
import KmdCmd
import KmdFiles
import mailbox
import time

import os
import logging

class KmdMboxMergeDateTree(KmdCmd.KmdCommand):

    def extendParser(self):
        super(KmdMboxMergeDateTree, self).extendParser()
        #Extend parser
        self.parser.add_argument('srctree', metavar='</path/to/srctree>', nargs=1, help='Path to merge')
        self.parser.add_argument('datetree', metavar='</path/to/datetree>', nargs=1, help='Root of a mbox date tree /aaaa/mm')
#        self.parser.add_argument('duptree', metavar='</path/to/datetree>', nargs=1, help='Root of a mbox date tree for duplicates /aaaa/mm')
        #FIXME : option for misc storage, default in /path/to/datetree/misc

    def run(self):
        srctree = self.args.srctree[0]
        datetree = self.args.datetree[0]
        filedestdatepattern = "%Y.sbd/%Y-%m"
        messagehashs = [] #Contiendra la liste des hashs connus
        mboxfiles = {} #dict path=> objet mbox
        doit = self.args.doit
        
        dupmboxname = "~duplicates.tmp"
        if os.path.exists(os.path.join(datetree, dupmboxname)):
            #Rename duplicates mbox to avoid huge overhead at runtime
            KmdFiles.fileMoveRename(os.path.join(datetree, dupmboxname), os.path.join(datetree, dupmboxname), doit)
     
        for root, dirs, files in os.walk(srctree):
            #For each folder in the src tree
            for name in files:
                dupcount, miscount, keepcount = 0,0,0
                #for each file in the folder
                p = os.path.join(root, name)
                if os.path.islink(p):
                    continue
                #Is it an mbox with meta datas ?
                if not KmdMbox.isFileMbox(p):
                    logging.debug("File %s is not a MBOX file", p)
                    continue
                srcbox = mailbox.mbox(p) #Open Mbox file
                logging.info("Opening MBOX %s", p)
                for m in srcbox : #Walk into Mbox
                    duplicate = False
                    #for each message
                    h = KmdMbox.messageHash(m) #hashmessage
                    if h in messagehashs :
                        #already known message
                        dupcount += 1
                        duplicate = True

                    vdate = KmdMbox.messageGetDate(m)
                    #Is the date valid
                    if vdate == None :
                        mboxname = os.path.join(datetree, "_misc_")
                        miscount += 1
                    else :
                        try :
                            mboxname = os.path.join(datetree, time.strftime(filedestdatepattern, vdate))
                            #Good, go on
                        except :
                            mboxname = os.path.join(datetree, "_misc_")
                            miscount += 1                        

                    if duplicate:
                        #current mbox : duplicates
                        mboxname = os.path.join(datetree, dupmboxname)
                        
                    if mboxname not in mboxfiles:
                        #File not already open
                        head, tail = os.path.split(mboxname)
                        if not os.path.exists(head) :
                            #new tree
                            if doit :
                                os.makedirs(head)
                            logging.debug("Creating %s tree", head)
                        #create or open mbox
                        if not os.path.exists(mboxname):
                            logging.info("Creating MBOX %s", mboxname)
                            if doit :
                                mboxfiles[mboxname] = mailbox.mbox(mboxname)
                            else :
                                mboxfiles[mboxname] = "foobar" #to fool mbox opening test
                                
                        else :
                            logging.info("Opening MBOX %s", mboxname)
                            mboxfiles[mboxname] = mailbox.mbox(mboxname)
                            #walk the mbox to append newhash
                            if not duplicate :
                                for m2 in mboxfiles[mboxname]:
                                    messagehashs.append(KmdMbox.messageHash(m2))
                            
                        #test against the newhashs
                        if not duplicate and h in messagehashs :
                            mboxname = os.path.join(datetree, dupmboxname)
                            dupcount += 1
                            if mboxname not in mboxfiles:
                                mboxfiles[mboxname] = mailbox.mbox(mboxname)
                    if doit :
                        KmdMbox.messageAddToMbox(mboxfiles[mboxname], m)

                    keepcount += 1
                    messagehashs.append(h)
                srcbox.close()
                logging.info("Closing MBOX %s - Duplicates: %d - Kept : %d (Misc : %d)", p, dupcount, keepcount, miscount)


if __name__ == "__main__":
    cmd = KmdMboxMergeDateTree(__doc__)
    cmd.run()

