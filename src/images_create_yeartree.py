#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Move image files from src into a yeartree (Good to prepare photo albums)"""

import KmdImages
import KmdFiles
import KmdCmd

import PIL.Image as Image
import os, sys
import logging

class KmdImagesCreateYearTree(KmdCmd.KmdCommand):
    def extendParser(self):
        super(KmdImagesCreateYearTree, self).extendParser()
        #Extend parser
        self.parser.add_argument('srctree', metavar='</path/to/srctree>', nargs=1, help='Path to images')
        self.parser.add_argument('yeartree', metavar='</path/to/yeartree>', nargs=1, help='Root of a date tree /aaaa/aaaammdd_hhmm.*')

    def run(self):
     
        for root, _, files in os.walk(self.args.srctree[0]):
            #For each folder in the src tree
            for name in files:
                #for each file in the folder
                p = os.path.join(root, name)
                #Is it an image with meta datas ?
                meta = KmdImages.readExivMetadata(p)
                if meta:
                    if "Exif.Photo.DateTimeOriginal" in meta.exif_keys :
                        d = meta["Exif.Photo.DateTimeOriginal"]
                    elif "Exif.Photo.DateTime" in meta.exif_keys :
                        d = meta["Exif.Photo.DateTime"]
                    else :
                        #FIXME : we could use the fstat modification time here
                        continue

                    #FIXME : Should we test the final date ?
                    try :
                        pathdest = os.path.join(self.args.yeartree[0], d.value.strftime("%Y"))
                        _, tail = os.path.splitext(name)
                        fdest = d.value.strftime("%Y%m%d_%H%M")+tail.lower()
                    except :
                        logging.warning("Wrong datetime value %s in %s", d.value, p)
                        continue
                    if not os.path.exists(pathdest):
                        logging.warning("%s does not exist", pathdest)
                        if self.args.doit :
                            os.makedirs(pathdest)
                    
                    KmdFiles.fileMoveRename(p, os.path.join(pathdest, fdest), self.args.doit)

                else :
                    logging.warning("%s has no metadatas, doesn't seem to be a photo !", p)                    


if __name__ == "__main__":
    cmd = KmdImagesCreateYearTree(__doc__)
    cmd.run()

