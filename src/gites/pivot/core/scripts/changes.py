# encoding: utf-8
"""
gites.pivot.core

Created by mpeeters
Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""

from gites.core.scripts.db import parseZCML

import argparse
import gites.pivot.core


def main():
    desc = 'Import changes from Pivot Database into GDW Database'
    parser = argparse.ArgumentParser(description=desc)
    args = parser.parse_args()
    parseZCML(gites.pivot.core, file='script.zcml')
    changes = PivotChanges(args)
    changes.process()


class PivotChanges(object):

    def __init__(self, args):
        self.args = args

    def process(self):
        pass
