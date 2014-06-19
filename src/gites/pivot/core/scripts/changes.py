# encoding: utf-8
"""
gites.pivot.core

Created by mpeeters
Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""

from affinitic.db.interfaces import IDatabase
from affinitic.db.utils import initialize_declarative_mappers, initialize_defered_mappers
from gites.core.scripts.db import parseZCML
from gites.db import DeclarativeBase
from gites.db.content import Hebergement
from gites.pivot.db.content import HebergementView
from sqlalchemy import select
from zope.component import getUtility

import argparse
import gites.pivot.core


def main():
    desc = 'Import changes from Pivot Database into GDW Database'
    parser = argparse.ArgumentParser(description=desc)
    args = parser.parse_args()
    parseZCML(gites.pivot.core, file='script.zcml')
    initializeDB()
    changes = PivotChanges(args)
    changes.process()


class PivotChanges(object):

    def __init__(self, args):
        self.args = args

    def process(self):
        pass

    def getHebergementsCGT(self):
        query = select([Hebergement.heb_code_cgt])
        return query.execute().fetchall()

    def getLastChanges(self, date):
        return HebergementView.get_last_changes(date)


def initializeDB():
    """
    Initialize db and mappers for script and return a session
    """
    pg = getUtility(IDatabase, 'postgres')
    session = pg.session
    initialize_declarative_mappers(DeclarativeBase, pg.metadata)
    initialize_defered_mappers(pg.metadata)
    return session
