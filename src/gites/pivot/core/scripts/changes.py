# encoding: utf-8
"""
gites.pivot.core

Created by mpeeters
Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""
from datetime import datetime

from affinitic.db.interfaces import IDatabase
from affinitic.db.utils import (initialize_declarative_mappers,
                                initialize_defered_mappers)
from gites.core.scripts.db import parseZCML
from gites.pivot.core.utils import (get_differences,
                                    now)
from gites.db import DeclarativeBase
from gites.db.content import (Hebergement,
                              Notification)
from gites.pivot.db.content import HebergementView
from zope.component import getUtility

import argparse
import gites.pivot.core

HEBCOLUMNS = ['heb_nom',
              'heb_adresse',
              'heb_localite',
              'heb_gps_long',
              'heb_gps_lat',
              'heb_nombre_epis',
              'heb_cgt_cap_min',
              'heb_cgt_cap_max',
              'heb_cgt_nbre_chmbre',
              'heb_descriptif_fr',
              'heb_descriptif_nl',
              'heb_descriptif_uk',
              'heb_descriptif_de',
              'heb_pointfort_fr',
              'heb_pointfort_nl',
              'heb_pointfort_uk',
              'heb_pointfort_de',
              'heb_gid_access_tous',
              'heb_animal',
              'heb_fumeur',
              'heb_lit_sup',
              'heb_lit_1p',
              'heb_lit_2p',
              'heb_lit_enf']

COMCOLUMNS = ['com_cp',
              'com_nom']

PROVCOLUMNS = ['prov_nom']

MAISCOLUMNS = ['mais_nom']


def main():
    desc = 'Import changes from Pivot Database into GDW Database'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('date', type=str,
                        help='Last Changes. Example: 2013/01/01')
    args = parser.parse_args()
    parseZCML(gites.pivot.core, file='script.zcml')
    initializeDB()
    changes = PivotChanges(args)
    changes.process()


class PivotChanges(object):

    def __init__(self, args):
        self.args = args
        date = self.args.date.split('/')
        self.date = datetime(int(date[0]),
                             int(date[1]),
                             int(date[2]), 0, 0, 0, 0)
        self.pg_session = getUtility(IDatabase, 'postgres').session

    def process(self):
        hebergements = self.compareGitesWithPivot() or []
        for heb in hebergements:
            for diff in heb['diff']:
                self.insertNotification(heb['table'],
                                        heb['pk'],
                                        diff[1],
                                        diff[2],
                                        diff[0])
            self.pg_session.commit()
        self.pg_session.close()

    def compareGitesWithPivot(self):
        code_cgt = self.getHebergementsCGT()
        code_cgt = [i.heb_code_cgt for i in code_cgt]
        hebsPivot = self.getLastChanges()
        hebsPivot = [i for i in hebsPivot if i.code_interne_CGT in code_cgt]
        hebergements = self.getHebergementsByCodeCgt([i.code_interne_CGT for i in hebsPivot])
        result = []
        for hebPivot in hebsPivot:
            heb = hebergements[hebPivot.code_interne_CGT]
            if heb:
                result.append({'table': 'hebergement',
                               'pk': str(heb.heb_pk),
                               'diff': get_differences(heb, hebPivot, HEBCOLUMNS)})
                if heb.commune:
                    result.append({'table': 'commune',
                                   'pk': str(heb.commune.com_pk),
                                   'diff': get_differences(heb.commune, hebPivot, COMCOLUMNS)})
                if heb.province:
                    result.append({'table': 'provinces',
                                   'pk': str(heb.province[0].prov_pk),
                                   'diff': get_differences(heb.province[0], hebPivot, PROVCOLUMNS)})
                if heb.maisonTourisme:
                    result.append({'table': 'maison_tourisme',
                                   'pk': str(heb.maisonTourisme[0].mais_pk),
                                   'diff': get_differences(heb.maisonTourisme[0], hebPivot, MAISCOLUMNS)})
        return result

    def insertNotification(self, table, pk, obj1, obj2, attr):
        notif = Notification(origin='PIVOT',
                             table=table,
                             column=attr,
                             table_pk=str(pk),
                             old_value=obj1,
                             new_value=obj2,
                             date=now(),
                             treated=None,
                             cmt=None,
                             user=None)
        self.pg_session.add(notif)

    def getHebergementsCGT(self):
        query = self.pg_session.query(Hebergement.heb_code_cgt)
        return query.all()

    def getHebergementsByCodeCgt(self, list):
        query = self.pg_session.query(Hebergement)
        query = query.filter(Hebergement.heb_code_cgt.in_(list))
        result = {}
        for i in query.all():
            result[i.heb_code_cgt] = i
        return result

    def getLastChanges(self):
        return HebergementView.get_last_changes(self.date)


def initializeDB():
    """
    Initialize db and mappers for script and return a session
    """
    pg = getUtility(IDatabase, 'postgres')
    session = pg.session
    initialize_declarative_mappers(DeclarativeBase, pg.metadata)
    initialize_defered_mappers(pg.metadata)
    return session
