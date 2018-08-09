#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Files utils.
Some scripts have been authored by Sebastien SAUVAGE <sebsauvage at sebsauvage dot net> http://sebsauvage.net/python/
"""

import logging
import datetime
import os
import os.path
import string
import sys
import sha
import time
import os
import sys
import shutil
from stat import *


def fileSHA(filepath):
    """ Compute SHA (Secure Hash Algorythm) of a file.
        Input : filepath : full path and name of file (eg. 'c:\windows\emm386.exe')
        Output : string : contains the hexadecimal representation of the SHA of the file.
                          returns '0' if file could not be read (file not found, no read rights...)
    """
    try:
        file = open(filepath, 'rb')
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


def treeDetectDoubles(directories):
    fileslist = {}
    # Group all files by size (in the fileslist dictionnary)
    for directory in directories:
        directory = os.path.abspath(directory)
        logging.info("Scanning directory %s", directory)
        os.path.walk(directory, handler_doubles, fileslist)

    logging.info('Comparing files...')
    # Remove keys (filesize) in the dictionnary which have only 1 file
    for (filesize, listoffiles) in fileslist.items():
        if len(listoffiles) == 1:
            del fileslist[filesize]

    # Now compute SHA of files that have the same size,
    # and group files by SHA (in the filessha dictionnary)
    filessha = {}
    ntotal = len(fileslist)
    n = 0

    while len(fileslist) > 0:
        (filesize, listoffiles) = fileslist.popitem()
        for filepath in listoffiles:
            sha = fileSHA(filepath)
            if filessha.has_key(sha):
                filessha[sha].append(filepath)
            else:
                filessha[sha] = [filepath]
        if n % 100 == 0:
            sys.stderr.write("%.2f %%\r" % (float(n*100)/float(ntotal)))
        n += 1

    if filessha.has_key('0'):
        del filessha['0']

    # Remove keys (sha) in the dictionnary which have only 1 file
    for (sha, listoffiles) in filessha.items():
        if len(listoffiles) == 1:
            del filessha[sha]
    return filessha


def handler_doubles(fileslist, directory, files):
    for fileName in files:
        filepath = os.path.join(directory, fileName)
        if os.path.isfile(filepath):
            filesize = os.stat(filepath)[6]
            if fileslist.has_key(filesize):
                fileslist[filesize].append(filepath)
            else:
                fileslist[filesize] = [filepath]


def get_modification_date(filename):
    t = os.path.getmtime(filename)
    return datetime.datetime.fromtimestamp(t)


def fileMoveRenameToDirIfOld(pname, dname, minage, doit=False):

    t = get_modification_date(pname)
    oldest = datetime.datetime.now()-datetime.timedelta(days=minage)
    if t < oldest:
        pathdest = os.path.join(dname, t.strftime("%Y/%m"))
        if not os.path.exists(pathdest):
            logging.warning("%s does not exist", pathdest)
            if doit:
                os.makedirs(pathdest)
        logging.debug("DEST TREE : %s", pathdest)
        fileMoveRenameToDir(pname, pathdest, doit)


def fileMoveRename(pname, dname, doit=False):
    count = 0
    head, tail = os.path.splitext(dname)
    while os.path.exists(dname):
        count += 1
        dname = os.path.join(head, '%s_(%d)%s' % (head, count, tail))
    logging.info("Move/rename %s to %s", pname, dname)
    if doit:
        shutil.move(pname, dname)


def fileMoveRenameToDir(pname, dest, doit=False):
    head, tail = os.path.split(pname)
    fileMoveRename(pname, os.path.join(dest, tail), doit)


def treeShrink(path, nbfiles=1, doit=False):
    for root, dirs, files in os.walk(path):
        logging.debug("Entering %s", root)
        if len(files) <= nbfiles and len(files) > 0 and len(dirs) == 0:
            logging.debug("Moving one level up file(s) from %s", root)
            for name in files:
                fileMoveRename(os.path.join(root, name), os.path.join(
                    root, "..", "%s_%s" % (root, name)), doit)
            logging.info("Rmdir %s", root)
            if doit:
                os.rmdir(root)


def removeEmptyFolders(path, doit=False):
    """Traverse tree and remove empty folders"""
    # FIXME : should use walk !
    if not os.path.isdir(path) or os.path.islink(path):
        return

    # remove empty subfolders
    try:
        files = os.listdir(path)
    except:
        logging.debug("Exception when listing dir %s", path)
        return

    if len(files):
        for f in files:
            fullpath = os.path.join(path, f)
            if os.path.isdir(fullpath) and not os.path.islink(path):
                removeEmptyFolders(fullpath, doit)

    # if folder empty, delete it
    files = os.listdir(path)
    if len(files) == 0:
        if os.path.islink(path):
            return
        logging.info("Removing empty folder %s", path)
        if doit:
            try:
                os.rmdir(path)
            except:
                logging.warn("Could not remove %s", path)
