#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Check all photos within a takeout dir and try to download the original file."""

import KmdImages
import KmdCmd
import KmdFiles

import PIL.Image as Image
import os, sys
import logging
import re
import json
import urllib

class KmdImagesCheckDateTree(KmdCmd.KmdCommand):
    def extendParser(self):
        super(KmdImagesCheckDateTree, self).extendParser()
        #Extend parser
        self.parser.add_argument('takeout', metavar='</path/to/takeout/Photos>', nargs=1, help='Root of a TakeOut tree')

    def run(self):
        doit = self.args.doit

        for root, _, files in os.walk(self.args.takeout[0]):
            #For each folder in the src tree

            for name in files:
                if not re.compile(r'.*\.json$').match(name):
                    #We want only json files to catch download urls
                    continue

                #for each file in the folder
                p = os.path.join(root, name)

                #load json
                try :
                    jf = open(p, 'r')
                    json_data = json.load(jf)
                except :
                    logging.warn("Could not open %s", p)
                    continue

                for m in json_data['media'] :
                    if 'url' in m :
                        if 'downloaded' not in m or not m['downloaded']:
                            # Download the file from `url` and save it locally if we didn't already download it
                            logging.info("Downloading %s from Google", m['title'].encode('utf-8').replace('/', '_'))
                            if doit :
                                try :
                                    urllib.urlretrieve(m['url'], os.path.join(root, m['title'].encode('utf-8').replace('/', '_')))
                                    m['downloaded'] = True
                                except :
                                    logging.warn("Can't get %s from %s", m['title'].encode('utf-8').replace('/', '_'), m['url'])

                if doit :
                    #save the downloaded list
                    with open(p, 'w') as jf :
                        jf.write(json.dumps(json_data, jf, indent=2))
                    logging.debug("Writing back json file : %s", p)

if __name__ == "__main__":
    cmd = KmdImagesCheckDateTree(__doc__)
    cmd.run()

