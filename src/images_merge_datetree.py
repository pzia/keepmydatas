#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Compare all photos within a tree with those stored in a date tree (yyyy/mm/dd/*) and remove already existing pictures"""

import KmdImages
import KmdCmd

import PIL.Image as Image
import os, sys
import logging

class KmdImagesMergeDateTree(KmdCmd.KmdCommand):
    def extendParser(self):
        super(KmdImagesMergeDateTree, self).extendParser()
        #Extend parser
        self.parser.add_argument('srctree', metavar='</path/to/srctree>', nargs=1, help='Path to images to merges')
        self.parser.add_argument('datetree', metavar='</path/to/datetree>', nargs=1, help='Root of a date tree /aaaa/mm/dd')
        #FIXME : we could/should add option to move photo file not matching the datetree.

    def run(self):
     
        ymd = {} #store path to ymd => list of potential matching files
        
        #Please note that is a WRONG good idea to store the PIL.Images in a dictionnary
        #Keep it simple and like this : just loading image when needed, and use the file system cache for performance.

        for root, dirs, files in os.walk(self.args.srctree[0]):
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
                        pathtest = os.path.join(self.args.datetree[0], d.value.strftime("%Y/%m/%d"))
                    except :
                        logging.warning("Wrong datetime value %s in %s", d.value, p)
                        continue
                        
                    if pathtest not in ymd :
                        ymd[pathtest] = []
                    ymd[pathtest].append(p)
                else :
                    logging.warning("%s has no metadatas, doesn't seem to be a photo !", p)                    

        logging.info("%d differents dates found", len(ymd))
        

        for pathtest in ymd :
            #KmdImage compare with folder in datetree
            if not os.path.exists(pathtest):
                logging.warning("%s does not exist", pathtest)
                continue

            for p in ymd[pathtest]:
                flist = os.listdir(pathtest)
                
                #We should at least first try to find an image with the same filename before crawling the whole directory
                head, tail = os.path.split(p)
                if tail in flist :
                    #In case both name matches !
                    logging.debug("%s found in flist", tail)
                    flist.insert(0, tail)
                elif tail.upper() in flist :
                    #In case both name matches !
                    logging.debug("%s found in flist", tail.upper())
                    flist.insert(0, tail.upper())
                elif tail.lower() in flist :
                    #In case both name matches !
                    logging.debug("%s found in flist", tail.lower())
                    flist.insert(0, tail.lower())

                for image in flist :
                    fullimage = os.path.join(pathtest, image)
                    logging.debug("Testing %s against %s", p, fullimage)
                    if KmdImages.compareImagesFiles(p, fullimage) :
                        logging.info("Image found in %s, removing %s", pathtest, p)
                        if self.args.doit :
                            os.remove(p)
                        break


if __name__ == "__main__":
    cmd = KmdImagesMergeDateTree(__doc__)
    cmd.run()

