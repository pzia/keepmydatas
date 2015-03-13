#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Mbox utils."""

import logging
import mailbox
#import rfc822
import datetime
import time
import email
import hashlib
import os
import re

magicmboxre = re.compile(r'^From .*$')

def messageHash(msg, keys = ['From', 'Cc', 'To', 'Date', 'Subject', 'Message-ID']):
    """Hash a message, regarding keys provided"""
    ho = hashlib.md5()
    ok, ko = 0, 0
    for kk in keys:
        if 0 and kk not in msg.keys() :
            k = kk.upper()
        else :
            k = kk
        if k in msg.keys():
            try :
                ho.update(msg[k].encode('ascii', errors='ignore').strip())
                ok += 1
            except :
                #FIXME: we should test how many component of the hash failed
                ho.update(k)
                logging.debug("Bad key %s in message", k)
                ko += 1
        else :
            logging.debug("No Key %s in message", k)
    return ho.digest()            
    
def messageDebug(m, header = None):
    if header is not None :
        logging.debug(header)
    for k in m.keys():
        logging.debug("%s => %s", k, m[k])
        
def messageAddToMbox(dbox, m, trashbox = None):
    """Add message to Mbox, and convet if required"""
    if trashbox == None :
        trashbox = dbox
    try :
        dbox.add(m)
    except UnicodeEncodeError :
        try :
            trashbox.add(m.as_string(True).encode('utf-8', errors='replace'))
            logging.warning("Force UTF message convert")                            
        except UnicodeEncodeError:
            trashbox.add(m.as_string(True).encode('ascii', errors='ignore'))
            logging.warning("Fallback to ASCII message convert")

def messageGetDate(m):
    vdate = None
    mdate = m['Date']
    #test known formats
    if mdate == "" or mdate == None : #dumb date !
        pass
    elif mdate[2] == "/": #english date
        try :
            vdate = time.strptime(mdate[:8], "%m/%d/%y")
        except :
            messageDebug(m)
    else : #defaut to RFC
        try :
            vdate = email.utils.parsedate(mdate)
            #FIXME: should we use _tz variant ?
        except:
            messageDebug(m)
    return vdate


def isFileMbox(path):
    magicline = ""
    try :
        if not os.path.exists(path):
            return False
        f = open(path)
        magicline = f.readline()
        f.close()
        return magicmboxre.match(magicline) != None
    except :
        logging.debug("Something went wrong when magic testing mbox candidate %s", path)
        logging.debug("First line was : %s", magicline)
        return False
