#! /usr/bin/env python
"""Extract zip
Arg1 : <path> #zip file path
Arg2 : <path> #where to extract
"""

import os
import sys
import zipfile


def extractZip(zpath, to):
    if not os.path.isfile(zpath):
        return
    if not os.path.isdir(to):
        return

    zf = zipfile.ZipFile(zf)
    zf.extractall(to)


if __name__ == "__main__":
    extractZip(sys.argv[1], sys.argv[2])
