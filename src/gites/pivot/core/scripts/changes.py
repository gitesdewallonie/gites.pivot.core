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
                                    get_best_match,
                                    now)
from gites.db import DeclarativeBase
from gites.db.content import Hebergement
from gites.db.content import Notification
from gites.db.content import Tarifs
from gites.db.content import Province
from gites.db.content import Commune
from gites.db.content import MaisonTourisme
from gites.db.content import Civilite
from gites.db.content import Notification

from gites.pivot.db.content import HebergementView
from gites.pivot.db.content import TarifView
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

PROCOLUMNS = ['pro_nom1',
              'pro_prenom1',
              'pro_adresse',
              'pro_tel_priv',
              'pro_fax_priv',
              'pro_gsm1',
              'pro_email',
              'pro_url']

CIVCOLUMNS = ['civ_titre']


def main():
    desc = 'Import changes from Pivot Database into GDW Database'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('date', type=str,
                        help='Last Changes. Example: 2013/01/01')
    parser.add_argument('origin', type=str,
                        choices=('PIVOT', 'GDW'),
                        help='Origin of the changes: PIVOT or GDW')
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
        self.origin = self.args.origin
        self.pg_session = getUtility(IDatabase, 'postgres').session
        self.mysql_session = getUtility(IDatabase, 'mysql').session

    def process(self):
        changes = []
        changes.extend(self.compareHebergements() or [])
        changes.extend(self.compareTarifs() or [])
        for change in changes:
            for diff in change['diff']:
                attr, obj1, obj2 = diff
                if not self.notifDeniedExists(change['table'],
                                              change['pk'],
                                              obj2,
                                              attr):
                    self.insertNotification(change['table'],
                                            change['pk'],
                                            obj1,
                                            obj2,
                                            attr)
            self.pg_session.commit()
        self.pg_session.close()

    def notifDeniedExists(self, table, pk, new_value, attr):
        query = self.pg_session.query(Notification)
        query = query.filter(Notification.origin == self.origin)
        query = query.filter(Notification.table == table)
        query = query.filter(Notification.column == attr)
        query = query.filter(Notification.table_pk == str(pk))
        query = query.filter(Notification.new_value == str(new_value))
        query = query.filter(Notification.treated == False)
        return query.count()

    def compareHebergements(self):
        origin_changes = self.getLastHebergementsChanges()
        dest_hebergements = self.getHebergementsByCodeCgt([i.heb_code_cgt for i in origin_changes])
        result = []
        for origin_change in origin_changes:
            dest_heb = dest_hebergements[origin_change.heb_code_cgt]
            if self.origin == 'PIVOT':
                gdw_heb = dest_heb
                pivot_heb = origin_change
            elif self.origin == 'GDW':
                gdw_heb = origin_change
                pivot_heb = dest_heb
            if gdw_heb:
                result.append({'table': 'hebergement',
                               'pk': str(gdw_heb.heb_pk),
                               'diff': get_differences(gdw_heb, pivot_heb, HEBCOLUMNS)})
                if gdw_heb.commune:
                    result.append({'table': 'commune',
                                   'pk': str(gdw_heb.commune.com_pk),
                                   'diff': get_differences(gdw_heb.commune, pivot_heb, COMCOLUMNS)})
                if gdw_heb.province:
                    result.append({'table': 'provinces',
                                   'pk': str(gdw_heb.province[0].prov_pk),
                                   'diff': get_differences(gdw_heb.province[0], pivot_heb, PROVCOLUMNS)})
                if gdw_heb.maisonTourisme:
                    result.append({'table': 'maison_tourisme',
                                   'pk': str(gdw_heb.maisonTourisme[0].mais_pk),
                                   'diff': get_differences(gdw_heb.maisonTourisme[0], pivot_heb, MAISCOLUMNS)})
        return result

    def compareTarifs(self):
        return
        origin_changes = self.getLastTarifsChanges()
        dest_hebergements = self.getHebergementsByCodeCgt([i.heb_code_cgt for i in origin_changes])
        result = []
        for origin_change in origin_changes:
            dest_heb = dest_hebergements[origin_change.heb_code_cgt]
            if self.origin == 'PIVOT':
                gdw_heb = dest_heb
                pivot_heb = origin_change
            elif self.origin == 'GDW':
                gdw_heb = origin_change
                pivot_heb = dest_heb
            if gdw_heb:
                # HEBERGEMENT
                result.append({'table': 'hebergement',
                               'pk': str(gdw_heb.heb_pk),
                               'diff': get_differences(gdw_heb, pivot_heb, HEBCOLUMNS)})
                # COMMUNE
                pivot_commune = get_best_match(self.pg_session, pivot_heb, Commune, COMCOLUMNS)
                result.append({'table': 'hebergement',
                               'pk': str(gdw_heb.heb_pk),
                               'diff': get_differences(gdw_heb.commune, pivot_commune, ['com_pk'])})
                # PROVINCE
                pivot_province = get_best_match(self.pg_session, pivot_heb, Province, PROVCOLUMNS)
                gdw_province = None
                if gdw_heb.province:
                    gdw_province = gdw_heb.province[0]
                result.append({'table': 'hebergement',
                               'pk': str(gdw_heb.heb_pk),
                               'diff': get_differences(gdw_province, pivot_province, ['prov_pk'])})
                # MAISON TOURISME
                pivot_tourisme = get_best_match(self.pg_session, pivot_heb, MaisonTourisme, MAISCOLUMNS)
                gdw_tourisme = None
                if gdw_heb.province:
                    gdw_tourisme = gdw_heb.maisonTourisme[0]
                result.append({'table': 'hebergement',
                               'pk': str(gdw_heb.heb_pk),
                               'diff': get_differences(gdw_tourisme, pivot_tourisme, ['mais_pk'])})
                # PROPRIO
                pivot_contact = pivot_heb.get_first_contact(self.mysql_session)
                result.append({'table': 'proprio',
                               'pk': str(gdw_heb.proprio.pro_pk),
                               'diff': get_differences(gdw_heb.proprio, pivot_contact, PROCOLUMNS)})
                # PROPRIO CIVILITE
                pivot_civilite = get_best_match(self.pg_session, pivot_contact, Civilite, CIVCOLUMNS)
                result.append({'table': 'hebergement',
                               'pk': str(gdw_heb.heb_pk),
                               'diff': get_differences(gdw_heb.proprio.civilite, pivot_civilite, ['civ_pk'])})
                # PROPRIO COMMUNE
                pivot_commune = get_best_match(self.pg_session, pivot_contact, Commune, COMCOLUMNS)
                result.append({'table': 'hebergement',
                               'pk': str(gdw_heb.heb_pk),
                               'diff': get_differences(gdw_heb.proprio.commune, pivot_commune, ['com_pk'])})
        return result

    def insertNotification(self, table, pk, obj1, obj2, attr):
        notif = Notification(origin=self.origin,
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

    def getHebergementsByCodeCgt(self, codes):
        if self.origin == 'PIVOT':
            mapper = Hebergement
            session = self.pg_session
        elif self.origin == 'GDW':
            mapper = HebergementView
            session = self.mysql_session

        query = session.query(mapper)
        query = query.filter(mapper.heb_code_cgt.in_(codes))
        result = {}
        for i in query.all():
            result[i.heb_code_cgt] = i
        return result

    def getLastHebergementsChanges(self):
        """
        Get last hebergements changes in origin DB for hebs that are in the 2 databases
        """
        if self.origin == 'PIVOT':
            gdw_hebs = self.pg_session.query(Hebergement.heb_code_cgt).all()
            gdw_hebs_cgt = [i.heb_code_cgt for i in gdw_hebs]
            last_changes = HebergementView.get_last_changes(self.date)
            last_changes = [i for i in last_changes if i.heb_code_cgt in gdw_hebs_cgt]
        elif self.origin == 'GDW':
            pivot_hebs = self.mysql_session.query(HebergementView.heb_code_cgt).all()
            pivot_hebs_cgt = [i.heb_code_cgt for i in pivot_hebs]
            last_changes = Hebergement.get_last_changes(self.date, session=self.pg_session, cgt_not_empty=True)
            last_changes = [i for i in last_changes if i.heb_code_cgt in pivot_hebs_cgt]
        return last_changes

    def getLastTarifsChanges(self):
        """
        Get last tarifs changes in origin DB for hebs that are in the 2 databases
        """
        if self.origin == 'PIVOT':
            # Attention je fais 2 fois cette requete
            gdw_hebs = self.pg_session.query(Hebergement.heb_code_cgt).all()
            gdw_hebs_cgt = [i.heb_code_cgt for i in gdw_hebs]
            last_changes = TarifView.get_last_changes(self.date)
            last_changes = [i for i in last_changes if i.heb_code_cgt in gdw_hebs_cgt]
        elif self.origin == 'GDW':
            pivot_hebs = self.mysql_session.query(HebergementView.heb_code_cgt).all()
            pivot_hebs_cgt = [i.heb_code_cgt for i in pivot_hebs]
            last_changes = Tarifs.get_last_changes(self.date, session=self.pg_session, cgt_not_empty=True)
            last_changes = [i for i in last_changes if i.hebergement.heb_code_cgt in pivot_hebs_cgt]
        return last_changes


def initializeDB():
    """
    Initialize db and mappers for script and return a session
    """
    pg = getUtility(IDatabase, 'postgres')
    session = pg.session
    initialize_declarative_mappers(DeclarativeBase, pg.metadata)
    initialize_defered_mappers(pg.metadata)
    return session
