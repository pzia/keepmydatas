#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shrink tree by moving standalone files one level up"""
import KmdCmd
import KmdFiles
import os
import logging

class KmdFilesMove(KmdCmd.KmdCommand):
    def extendParser(self):
        super(KmdFilesMove, self).extendParser()
        #Extend parser
        self.parser.add_argument('tree', metavar='</path/to/src>', nargs=1, help='The source Tree')
        self.parser.add_argument('--count', metavar='<integer>', default=1, help='Number of files to make tree shrinking')
        
    def run(self):
        KmdFiles.treeShrink(self.args.tree[0], int(self.args.count), self.args.doit)

if __name__ == "__main__":
    KmdFilesMove(__doc__).run()
