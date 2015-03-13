#!/usr/bin/python

import os, os.path, string, sys, sha
import time, os, sys
from stat import *

message = """
doublesdetector.py 1.0p

This script will search for files that are identical
(whatever their name/date/time).

  Syntax : python %s <directories>

      where <directories> is a directory or a list of directories
      separated by a semicolon (;)

Examples : python %s c:\windows
           python %s c:\;d:\;e:\ > doubles.txt
           python %s c:\program files > doubles.txt

This script is public domain. Feel free to reuse and tweak it.
The author of this script Sebastien SAUVAGE <sebsauvage at sebsauvage dot net>
http://sebsauvage.net/python/
Adaptation from Hugues Bernard
""" % ((sys.argv[0], )*4)

def fileSHA ( filepath ) :
    """ Compute SHA (Secure Hash Algorythm) of a file.
        Input : filepath : full path and name of file (eg. 'c:\windows\emm386.exe')
        Output : string : contains the hexadecimal representation of the SHA of the file.
                          returns '0' if file could not be read (file not found, no read rights...)
    """
    try:
        file = open(filepath,'rb')
        digest = sha.new()
        data = file.read(65536)
        while len(data) != 0:
            digest.update(data)
            data = file.read(65536)
        file.close()
    except:
        return '0'
    else:
        return digest.hexdigest()

def detectDoubles( directories ):
    fileslist = {}
    # Group all files by size (in the fileslist dictionnary)
    for directory in directories:
        directory = os.path.abspath(directory)
        sys.stderr.write('Scanning directory '+directory+'...')
        os.path.walk(directory,callback,fileslist)
        sys.stderr.write('\n')

    sys.stderr.write('Comparing files...\n')
    # Remove keys (filesize) in the dictionnary which have only 1 file
    for (filesize,listoffiles) in fileslist.items():
        if len(listoffiles) == 1:
            del fileslist[filesize]

    # Now compute SHA of files that have the same size,
    # and group files by SHA (in the filessha dictionnary)
    filessha = {}
    ntotal = len(fileslist)
    n = 0

    while len(fileslist)>0:
        (filesize,listoffiles) = fileslist.popitem()
        for filepath in listoffiles:
            sha = fileSHA(filepath)
            if filessha.has_key(sha):
                filessha[sha].append(filepath)
            else:
                filessha[sha] = [filepath]
        if n % 100 == 0:
            sys.stderr.write("%.2f %%\r" % (float(n*100)/float(ntotal)) )
        n+=1

    if filessha.has_key('0'):
        del filessha['0']

    # Remove keys (sha) in the dictionnary which have only 1 file
    for (sha,listoffiles) in filessha.items():
        if len(listoffiles) == 1:
            del filessha[sha]
    sys.stderr.write('\n')
    return filessha

def callback(fileslist,directory,files):
    sys.stderr.write('.')
    for fileName in files:
        filepath = os.path.join(directory,fileName)
        if os.path.isfile(filepath):
            filesize = os.stat(filepath)[6]
            if fileslist.has_key(filesize):
                fileslist[filesize].append(filepath)
            else:
                fileslist[filesize] = [filepath]

import os
import datetime
def modification_date(filename):
    t = os.path.getmtime(filename)
    return datetime.datetime.fromtimestamp(t)

if __name__ == "__main__":

    if len(sys.argv) == 2 :
        doubles = detectDoubles(sys.argv[1].split(';'))
        print 'The following files are identical:'
        for filesha in doubles.keys():
            print('\n---')
            for p in doubles[filesha]:
                print p, modification_date(p)
    #    print '\n'.join(["----\n%s" % '\n'.join(doubles[filesha]) for filesha in doubles.keys()])
        print '----'
    elif len(sys.argv) == 3 :
        cmppath = sys.argv[1].split(';')
        delpath = sys.argv[2].split(';')
        print "Matching files in %s" % cmppath
        print "Deleting files matching any of the following %s" % delpath
        doubles = detectDoubles(cmppath)

        for fsha in doubles.keys():
            ftodel = []
            mintime = time.time()
            maxtime = 0
            maxlevel = 0
            maxpathsize = 0
            filesha = fsha

            for p in doubles[filesha]:
                st = os.stat(p)
                atime = st[ST_ATIME] #access time
                mtime = st[ST_MTIME] #modification time
                mintime = min(mintime, atime, mtime)
                maxtime = max(maxtime, atime, mtime)
                maxlevel = max(maxlevel, len(p.split('/')))
                maxpathsize = max(maxpathsize, len(p))
            for p in doubles[filesha]:
                try :
                    os.utime(p,(maxtime,mintime))
                except :
                    print "Couldn't not set min timestamp, still going on"

            for path in doubles[fsha]:
                for dpath in delpath:
                    if path.find(dpath) == 0:
                        ftodel.append(path)
            if len(ftodel) < len(doubles[fsha]):
                for path in ftodel:
                    try :
                        os.remove(path)
                        print "Removing %s" % path
                    except:
                        print "ERROR removing %s" % path
            else:
                print "Keeping %s" % ftodel
    else:
        print message
