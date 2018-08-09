#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compare all photos within a date tree (yyyy/mm/dd/*) and check date time with filename's pattern"""

import KmdImages
import KmdCmd
import KmdFiles

import PIL.Image as Image
import os
import sys
import re
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

        knownpatterns = [
            r'\w*(\d\d\d\d)(\d\d)(\d\d)[_t]\d\d\d\d\d.*?\.jpg',
            r'(\d\d\d\d)-(\d\d)-(\d\d) \d\d\.\d\d\.\d\d.*?\.jpg',
            r'img(\d\d)(\d\d)(\d\d)-\d\d\d\d.*?\.jpg',
        ]

        rekp = []
        for k in knownpatterns:
            rekp.append(re.compile(k, re.I))

        logging.warn("Quarantine into : %s", self.args.quarantine[0])

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
                        dexifstr = d.value.strftime("%Y/%m/%d")
                        pathdest = os.path.join(
                            self.args.datetree[0], dexifstr)
                    except:
                        logging.warning(
                            "Wrong datetime value %s in %s", d.value, p)
                        KmdFiles.fileMoveRenameToDir(
                            p, self.args.quarantine[0], self.args.doit)
                        continue

                    for rk in rekp:
                        m = rk.match(name)
                        if m != None:
                            yy = m.groups()[0]
                            mm = m.groups()[1]
                            dd = m.groups()[2]
                            if len(yy) == 2:
                                yy = "20%s" % yy
                            dnamestr = "%s/%s/%s" % (yy, mm, dd)
                            if dnamestr != dexifstr:
                                logging.info(
                                    "Dates don't match for %s - Exif %s != Name %s", p, dexifstr, dnamestr)
                                if d.value.strftime('%y') != yy[-2:]:
                                    logging.warn(
                                        "Year do not match for %s !", p)
                                d.value = d.value.strptime(
                                    dnamestr+d.value.strftime(":%H:%M"), "%Y/%m/%d:%H:%M")
                                logging.info(
                                    "Setting new exif|v date to %s", d.value)
                                if self.args.doit:
                                    meta[d.key] = d
                                    meta.write()
                            continue

                    if pathdest not in ymd:
                        ymd[pathdest] = []
                    ymd[pathdest].append(p)
                else:
                    logging.warning(
                        "%s has no metadatas, doesn't seem to be a photo !", p)
                    KmdFiles.fileMoveRenameToDir(
                        p, self.args.quarantine[0], self.args.doit)

        logging.info("%d differents dates found", len(ymd))


if __name__ == "__main__":
    cmd = KmdImagesCheckDateTree(__doc__)
    cmd.run()
