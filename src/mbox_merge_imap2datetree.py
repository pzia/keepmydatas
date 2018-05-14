#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compare all messages within an imaps account with those stored in a date tree (yyyy/mm)"""

import KmdMbox
import KmdCmd
import mailbox
import imaplib
import time

import os
import logging

class KmdMboxMergeImapDateTree(KmdCmd.KmdCommand):

    def extendParser(self):
        super(KmdMboxMergeImapDateTree, self).extendParser()
        #Extend parser
        self.parser.add_argument('account', metavar='<username@hostname:991/path/to/folder>', nargs=1, help='imaps account')                
        self.parser.add_argument('datetree', metavar='</path/to/datetree>', nargs=1, help='Root of a mbox date tree /aaaa/mm')
        #FIXME : option for duplicate storage, default in /path/to/datetree/duplicates
        #FIXME : option for misc storage, default in /path/to/datetree/misc
        
    def parseAccount(self):
        account = self.args.account[0]
        at = account.find('@')
        assert(at > 0)
        colonpw = account.find(':')
        assert(colonpw > 0)
        slash = account.find('/')
        assert(slash > 0)
        colonport = account.find(':', colonpw+1)
        assert(colonport > 0)
        username = account[0:colonpw]
        password = account[colonpw+1:at]
        hostname = account[at+1:colonport]
        port = account[colonport+1:slash]
        srcpath = account[slash+1:]
        logging.debug("Connexions parms : %s, %s, %s, %s, %s" % (username, password, hostname, port, srcpath))
        return username, password, hostname, port, srcpath

    def run(self):
        username, password, hostname, port, srcpath  = self.parseAccount()
        logging.info("Connecting : %s, %s, %s, %s, %s" % (username, password, hostname, port, srcpath))
        datetree = self.args.datetree[0]
        filedestdatepattern = "%Y.sbd/%Y-%m"
        messagehashs = []
        mboxfiles = {}
        doit = self.args.doit
        dupcount, miscount, keepcount = 0,0,0

        M = imaplib.IMAP4_SSL(hostname, port)
        M.login(username, password)
        M.select(srcpath)
        typd, data = M.search(None, 'ALL')
        
        for num in data[0].split():
            typ, dat = M.fetch(num, '(RFC822)')
            logging.debug('Message %s' % num)
#            print(dat)
            m = mailbox.Message(dat[0][1])
            duplicate = False
            #for each message
            h = KmdMbox.messageHash(m) #hashmessage
            if h in messagehashs :
                #already known message
                dupcount += 1
                duplicate = True

            vdate = KmdMbox.messageGetDate(m)
            if vdate == None :
                mboxname = os.path.join(datetree, "_misc_")
                miscount += 1
            else :
                mboxname = os.path.join(datetree, time.strftime(filedestdatepattern, vdate))

            if duplicate:
                mboxname += ".dup"
                
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
                    mboxname += ".dup"
                    dupcount += 1
                    if mboxname not in mboxfiles:
                        mboxfiles[mboxname] = mailbox.mbox(mboxname)
            if doit :
                KmdMbox.messageAddToMbox(mboxfiles[mboxname], m)

            keepcount += 1
            messagehashs.append(h)
#                srcbox.close()
#                logging.info("Closing MBOX %s - Duplicates: %d - Kept : %d (Misc : %d)", p, dupcount, keepcount, miscount)


if __name__ == "__main__":
    cmd = KmdMboxMergeImapDateTree(__doc__)
    cmd.run()

