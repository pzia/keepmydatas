#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Template of command line script"""

import argparse
import logging


class KmdCommand(object):
    parser = None
    args = None

    def __init__(self, desc):
        self.createParser(desc)
        self.setLogging()
        # self.run()

    def createParser(self, description):
        """Create the basic command line parser"""
        self.parser = argparse.ArgumentParser(description=description)
        self.extendParser()
        self.args = self.parser.parse_args()

    def extendParser(self):
        self.parser.add_argument('--doit', action="store_true",
                                 help='Mandatory flag to perform the actual work (Do it !)')
        self.parser.add_argument(
            '--debug', action="store_true", help='Set logging to debug mode')
        self.parser.add_argument(
            '--info', action="store_true", help='Set logging to info mode')
        self.parser.add_argument(
            '--warn', action="store_true", help='Set logging to warning mode')

    def setLogging(self):
        if self.args.debug:  # Set Debug mode
            logging.basicConfig(level=logging.DEBUG)
            logging.debug("Debug Mode")
        elif self.args.info:
            logging.basicConfig(level=logging.INFO)
        elif self.args.warn:
            logging.basicConfig(level=logging.WARNING)
        else:
            logging.basicConfig(level=logging.INFO)

    def run(self):
        pass
