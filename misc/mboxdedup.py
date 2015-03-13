# -*- coding: utf-8 -*-
# paparazzia@gmail.com

import sys
import mailbox
#import rfc822
import datetime
import time
import email
import hashlib
import os

if not (len(sys.argv) > 1) :
    print("Usage : dedup.py srcdir destdir")
    sys.exit() 

destmboxs = {}
destmboxs['duplicates'] = mailbox.mbox(os.path.join(sys.argv[2], "duplicates"))
destmboxs['misc'] = mailbox.mbox(os.path.join(sys.argv[2], "misc"))
hm = []

def addmbox(dbox, m, trashbox = None):
    if trashbox == None :
        trashbox = dbox
    try :
        dbox.add(m)
    except UnicodeEncodeError :
        try :
            trashbox.add(m.as_string(True).encode('utf-8', errors='replace'))
            print("UTF")                            
        except UnicodeEncodeError:
            trashbox.add(m.as_string(True).encode('ascii', errors='ignore'))
            print("NOT BAD")
#                except UnicodeEncodeError:
#                    print("---NO WAY")
                

def myhash(dico, keys = ['From', 'To', 'Date', 'Subject', 'Message-ID']):
    ho = hashlib.md5()
    for k in keys:
        if k in dico.keys():
            try :
                ho.update(dico[k].encode('utf-8', errors='ignore'))
            except :
                pass
    return ho.digest()            
    
def debugMessage(f, m):
    print("--%s--" % f)
    for k in m.keys():
        print(k, "=>", m[k])  


#Walking over SRC

errorcount = 0
good = 0
stored = 0
oldgood, oldstored = 0, 0

for d in os.walk(sys.argv[1]):
    for f in d[2]:
        if ".msf" in f or ".wdseml" in f:
            print("Excluding %s" % f)
            continue
        mfile = os.path.join(d[0], f)
        srcbox = mailbox.mbox(mfile)
        
        #Iterating over srcbox
        for m in srcbox :
            if errorcount > 10 :
                sys.exit()
            #récupère la date
            mdate = m['Date']
            #hash
            h = myhash(m)
            #compare
            if h in hm:
                addmbox(destmboxs['duplicates'],m)                
                continue
            vdate = None
            #test known formats
            if mdate == "" or mdate == None : #dumb date !
                pass
            elif mdate[2] == "/": #english date
                try :
                    vdate = time.strptime(mdate[:8], "%m/%d/%y")
                except :
                    errorcount += 1
                    print("++%s++" % mdate[:8])
                    debugMessage(f, m)
            else : #defaut to RFC
                try :
                    vdate = email.utils.parsedate_tz(mdate)
                except:
                    errorcount += 1
                    debugMessage(f, m)
            if vdate == None :
                sdate = "misc"
            else :
                good += 1
                sdate = time.strftime("%Y-%m", vdate)
              
            if not sdate in destmboxs.keys():
                destmboxs[sdate] = mailbox.mbox(os.path.join(sys.argv[2], sdate))
            addmbox(destmboxs[sdate], m)
            hm.append(h)
            stored += 1            
        srcbox.close()            
        print("File : %s - Good %d - Stored %d" % (f, good, stored))
        if good == oldgood and stored == oldstored :
            print("Remove %s" % mfile)
            os.remove(mfile)
        oldgood, oldstored = good, stored
        
sys.exit()
destination = mailbox.mbox('mboxdest')
d2 = mailbox.mbox("d2")
destination.lock()
c = 0


for f in sys.argv[1:]:
    mb = mailbox.mbox(f, None, False)
#nmb = mailbox.mbox('/home/hbernard/ToSentTEST.mbox', None, True)
    for m in mb :
        h = hashlib.md5(m.as_string(True).encode('utf-8').strip()).digest()
        if h in hm:
            print("Duplicate : %s" % m['Subject'])
            continue
        if "COMM" in m['Subject']:
            print("PING")
            d2.add(m.as_string(True))
        print("ADDING : %s - %s" % (h, m['Subject']))
        destination.add(m.as_string(True))
        c+=1
        hm.append(h)
print("Messages %d" % c)
destination.flush()
destination.unlock()
destination.close()

destination = mailbox.mbox('mboxdest')
for m in destination :
    print("%s" % m['Subject'])

sys.exit()

now = datetime.datetime.now()

print("Messages to push : ", len(mb))
#print("Time is now : ", now.utctimetuple(), email.utils.formatdate(time.mktime(now.timetuple())))

