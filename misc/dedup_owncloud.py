#!/usr/bin/python
# -*- coding: latin-1 -*-

#Search for _conflict- files and remove false positive

import os.path
import re
import hashlib
import sys 

#./CTR_F000_conflict-20130213-035414.TXT

owncloudre = re.compile(r'^(.*)(_conflict-\d{8}-\d{6})(.*)$')

def md5Checksum(filePath):
    fh = open(filePath, 'rb')
    m = hashlib.md5()
    while True:
        data = fh.read(8192)
        if not data:
            break
        m.update(data)
    return m.hexdigest()

def unconflict_directory(path):
    print("Running in %s" % path) 
    for root, dirs, files in os.walk(path): 
        for i in files:
            m = owncloudre.match(i)
            if m != None :
                parts = m.groups()
                origname = "%s%s" % (parts[0], parts[2])
                origpath = os.path.join(root, origname)
                curpath = os.path.join(root, i)
                if not os.path.isfile(origpath):
                    print("RENAME: %s doesn't exist anymore" % origpath)
                    os.rename(curpath, origpath)
                    continue
                if md5Checksum(origpath) == md5Checksum(curpath):
                    print("REMOVE: %s" % curpath)
                    os.remove(curpath)
                else :
                    print("KEEP: %s != %s" % (origpath, curpath))

if __name__ == '__main__':
    if len(sys.argv) > 1:
        for p in sys.argv[1:]:
            unconflict_directory(p)
