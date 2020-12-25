#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Detect same images and try to merge metadatas before deleting duplicates"""

import PIL.Image as Image
import PIL.ImageChops as ImageChops
import sys
import os
import pyexiv2
import datetime
import logging

#Handler for merging properties

def handler_mergeList(a, b):
    """List merger"""
    #FIXME : there is certainly a better python way !
    for p in b :
        if p not in a:
            a.append(p)
    return a
    
def handler_minDate(a, b):
    """Minimum date"""
    if a < b :
        return a
    else :
        return b

def handler_keepMain(a, b):
    """Keep left"""
    return a

def handler_Exif_Image_Orientation(a, b):
    """Assert : the higher is better, mainly because 1 is 'no orientation'"""
    if a > b :
        return a
    else :
        return b

def handler_concat(a, b):
    return (a+b)
    
def handler_Iptc_Application2_ProgramVersion(a, b):
    try :
        la = [int(x) for x in a[0].split(".")]
        lb = [int(x) for x in b[0].split(".")]
        if la > lb :
            return [".".join([str(x) for x in la])]
        else :
            return [".".join([str(x) for x in lb])]
    except :
        if a > b :
            return a
        else :
            return b

exiv_changed_keywords = ["merged_kmd"] #Tag set when pictures are merged (if IPTC is in use)

#Match exif/iptc properties to do the merge
exiv_handlers = {
    #Keep left (main pictures)
    "Iptc.Application2.ProgramVersion" : handler_Iptc_Application2_ProgramVersion,
    "Exif.Image.Software" : handler_keepMain,
    #Concat
    "Exif.Photo.UserComment" : handler_concat,
    #Lists
    "Iptc.Application2.Keywords" : handler_mergeList,
    #Orientation
    "Exif.Image.Orientation" : handler_Exif_Image_Orientation,
    "Exif.Thumbnail.Orientation" : handler_Exif_Image_Orientation,
    #Dates
    "Exif.Image.DateTime" : handler_minDate,
    "Exif.Photo.DateTimeOriginal" : handler_minDate,
}

#Don't try to do anything with these properties
exiv_ignored_properties = ["Exif.Thumbnail.JPEGInterchangeFormat", "Exif.Image.ExifTag", "Exif.Photo.InteroperabilityTag", "Exif.Photo.MakerNote", "Exif.MakerNote.Offset"]

def comparePilImages(img1, img2):
    """Compare 2 PIL.Images and return True if there is no difference"""
    try :
        diff = ImageChops.difference(img1, img2)
        bbox = diff.getbbox()
        del(diff)
    except :
        return False
    return bbox == None

def compareImagesFiles(f1, f2):
    """Load two files in PIL, and compare"""
    img1 = Image.open(f1)
    img2 = Image.open(f2)
    return comparePilImages(img1, img2)

def compareImagesFolder(folder, quick = False):
    """Compare images in a folder"""
    logging.debug("Comparing images in %s", folder)
    files = [os.path.join(folder, x) for x in os.listdir(folder)]

    return compareImagesCollection(files, quick)    
    
def compareImagesCollection(files, quick = True):
    imgf = []
    samef = []

    for fpath in files :
        if not os.path.isfile(fpath):
            #Only try to load files !
            logging.info("Not a file : %s" % fpath)
            continue
        try:
            Image.open(fpath)
            imgf.append(fpath)
        except:
            logging.info("Not an image : %s" % fpath)
            pass

    for f1 in imgf:
      imgf1 = Image.open(f1)
      for f2 in imgf:
        if f2 <= f1 :
            continue
        if quick and abs(os.path.getsize(f1) - os.path.getsize(f2)) > 1000 :
            continue
        imgf2 = Image.open(f2)
        if comparePilImages(imgf1, imgf2):
            logging.debug("Match Images : %s = %s", f1, f2)
            found = False
            for fl in samef:
                #FIXME : Should rewrite this !
                if f1 in fl and f2 in fl :
                    found = True
                    break
                if f1 in fl:
                    fl.append(f2)
                    found = True
                    break
                if f2 in fl:
                    fl.append(f1)
                    found = True
                    break
            if not found :
                #Images are the same, but not already matched
                samef.append([f1,f2])

    del(imgf)

    return(samef)

def readExivMetadata(path):
    try :
        meta = pyexiv2.ImageMetadata(path)
        meta.read()
        return meta
    except :
        logging.debug("This file has no exiv metadatas : %s", path)
        return False
    
def mergeExivMetadata(sameImages, doit = False):
    #FIXME : should be clevier to choose the mainImage
    write = False
    mainI = sameImages[0]
    metas = {}
    for pathI in sameImages:
        meta = pyexiv2.ImageMetadata(pathI)
        meta.read()
        metas[pathI] = meta

    for pathI in sameImages[1:]:
        logging.debug("Comparing %s and %s", mainI, pathI)
        for k in metas[pathI].iptc_keys + metas[pathI].exif_keys:
            if k in exiv_ignored_properties:
                continue
            newval = None
            if k in metas[mainI].iptc_keys + metas[mainI].exif_keys :
                try :
                    if metas[mainI][k].value != metas[pathI][k].value : 
                        logging.debug("Difference for %s", k)
                        logging.debug("%s <> %s", metas[mainI][k].value, metas[pathI][k].value)
                        if k in exiv_handlers :
                            newval = exiv_handlers[k](metas[mainI][k].value, metas[pathI][k].value)
                            logging.info("Merged property %s : %s", k, newval)
                        else :
                            logging.warn("NO HANDLER for %s", k)
                except :
                    logging.warn("Coulnd't compare %s exif property for %s", k, mainI)
            else :
                newval = metas[pathI][k].value
                logging.info("Imported property %s : %s", k, newval)
          
            if newval != None :
                try :
                    metas[mainI][k] = newval
                    write = True
                except :
                    logging.warn("Coulnd't setup %s exif property for %s", k, mainI)
    if write :
        if "Iptc.Application2.Keywords" in metas[mainI].iptc_keys:
            metas[mainI]["Iptc.Application2.Keywords"] = handler_mergeList(metas[mainI]["Iptc.Application2.Keywords"].value, exiv_changed_keywords)
        logging.info("Writing properties to %s", mainI)
        if doit :
            metas[mainI].write()
    for f in sameImages[1:] :
        logging.info("Removing %s", f)
        if doit :
            os.remove(f)
    for m in metas.keys():
        del(metas[m])
    del(metas)
            
def cleanDir(folder, doit = False, quick = True):
    logging.info("Cleaning %s", folder)
    samef = compareImagesFolder(folder, quick = True)
    for s in samef :
        mergeExivMetadata(s, doit)
    del(samef)

    for f in os.listdir(folder):
        p = os.path.join(folder, f)

        if os.path.isdir(p):
            logging.debug("Testing %s", p)        
            cleanDir(p, doit, quick = True)

