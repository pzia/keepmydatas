#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compare all photos within a date tree (yyyy/mm/dd/*) and remove images without metadatas"""

import KmdImages
import KmdCmd
import KmdFiles

import PIL.Image as Image
import os
import sys
import logging


class KmdImagesCheckDateTree(KmdCmd.KmdCommand):
    def extendParser(self):
        super(KmdImagesCheckDateTree, self).extendParser()
        # Extend parser
        self.parser.add_argument('datetree', metavar='</path/to/datetree>',
                                 nargs=1, help='Root of a date tree /aaaa/mm/dd')
        self.parser.add_argument('quarantine', metavar='</path/to/directory>',
                                 nargs=1, help='Path to move suspicious files')

    def run(self):

        ymd = {}  # store path to ymd => list of potential matching files

        # Please note that is a WRONG good idea to store the PIL.Images in a dictionnary
        # Keep it simple and like this : just loading image when needed, and use the file cache for performance.
        logging.warn(self.args.quarantine[0])

        for root, dirs, files in os.walk(self.args.datetree[0]):
            # For each folder in the src tree
            quarantine = False
            for name in files:
                # for each file in the folder
                p = os.path.join(root, name)
                # Is it an image with meta datas ?
                meta = KmdImages.readExivMetadata(p)
                if meta:
                    if "Exif.Photo.DateTimeOriginal" in meta.exif_keys:
                        d = meta["Exif.Photo.DateTimeOriginal"]
                    elif "Exif.Photo.DateTime" in meta.exif_keys:
                        d = meta["Exif.Photo.DateTime"]
                    else:
                        logging.info("%s without date" % p)
                        KmdFiles.fileMoveRenameToDir(
                            p, self.args.quarantine[0], self.args.doit)
                        continue

                    # FIXME : Should we test the final date ?
                    try:
                        pathtest = os.path.join(
                            self.args.datetree[0], d.value.strftime("%Y/%m/%d"))
                    except:
                        logging.warning(
                            "Wrong datetime value %s in %s", d.value, p)
                        KmdFiles.fileMoveRenameToDir(
                            p, self.args.quarantine[0], self.args.doit)
                        continue

                    if pathtest not in ymd:
                        ymd[pathtest] = []
                    ymd[pathtest].append(p)
                else:
                    logging.warning(
                        "%s has no metadatas, doesn't seem to be a photo !", p)
                    KmdFiles.fileMoveRenameToDir(
                        p, self.args.quarantine[0], self.args.doit)

        logging.info("%d differents dates found", len(ymd))


if __name__ == "__main__":
    cmd = KmdImagesCheckDateTree(__doc__)
    cmd.run()
