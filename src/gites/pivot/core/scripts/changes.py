# encoding: utf-8
"""
gites.pivot.core

Created by mpeeters
Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""

from affinitic.db.interfaces import IDatabase
from affinitic.db.utils import (initialize_declarative_mappers,
                                initialize_defered_mappers)
from gites.core.scripts.db import parseZCML
from gites.pivot.core.utils import get_differences
from gites.db import DeclarativeBase
from gites.db.content import Hebergement
from gites.pivot.db.content import HebergementView
from zope.component import getUtility

import argparse
import gites.pivot.core

HEBCOLUMNS = ['heb_nom',
              'heb_adresse',
              'com_cp',
              'heb_localite',
              'com_nom',
              'prov_nom',
              'heb_maison_tourisme_fk',
              'heb_gps_long',
              'heb_gps_lat',
              'heb_nombre_epis',
              'heb_cgt_cap_min',
              'heb_cgt_cap_max',
              'heb_cgt_nbre_chmbre',
              'heb_descriptif',
              'heb_descriptif_nl',
              'heb_descriptif_uk',
              'heb_descriptif_de',
              'heb_pointfort',
              'heb_pointfort_nl',
              'heb_pointfort_uk',
              'heb_pointfort_de',
              'heb_gid_access_tous',
              'heb_animal',
              'heb_fumeur',
              'heb_date_creation',
              'heb_date_modification',
              'heb_lit_sup',
              'heb_lit_1p',
              'heb_lit_2p',
              'heb_lit_enf']


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
        self.pg_session = getUtility(IDatabase, 'postgres').session

    def process(self):
        differences = self.compareGitesWithPivot() or []
        for diff in differences:
            self.insertNotification(diff[1],
                                    diff[2],
                                    diff[0])

    def compareGitesWithPivot(self):
        # XXX Changer la date
        from datetime import datetime
        self.getHebergementsCGT()
        hebsPivot = self.getLastChanges(datetime.now())
        for hebPivot in hebsPivot:
            heb = Hebergement.first(heb_code_cgt=hebPivot.heb_code_cgt)
            if heb:
                return get_differences(heb, hebPivot, HEBCOLUMNS)

    def insertNotification(self, obj1, obj2, attr):
        pass

    def getHebergementsCGT(self):
        query = self.pg_session.query(Hebergement.heb_code_cgt)
        return query.all()

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
