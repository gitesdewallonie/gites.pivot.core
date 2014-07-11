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
from gites.db.content import Proprio

from gites.pivot.db.content import HebergementView
from gites.pivot.db.content import TarifView
from gites.pivot.db.content import ContactView
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

TARIFCOLUMNS = ['min',
                'max',
                'cmt']

TARIF_TYPES_CORRESPONDANCE = {
    u"Basse saison - (Mid-week)": ('', ''),
    u"Basse saison - (Semaine)": ('LOW_SEASON', 'WEEK'),
    u"Basse saison - (Week-end)": ('LOW_SEASON', 'WEEKEND'),
    u"Chambre 1 personne + petit déjeuner / nuit": ('', ''),
    u"Chambre 1 personne sans petit déjeuner / nuit": ('ROOM', '1_PERSON'),
    u"Chambre 2 personne sans petit déjeuner / nuit": ('ROOM', '2_PERSONS'),
    u"Chambre 2 personnes + petit déjeuner / nuit": ('', ''),
    u"Chambre 3 personnes + petit déjeuner / nuit": ('', ''),
    u"Chambre 4 personnes + petit déjeuner / nuit": ('', ''),
    u"Chambre sans petit déjeuner / nuit": ('', ''),
    u"Charges": ('', ''),
    u"Charges en calcul forfaitaire": ('CHARGES', 'INCLUSIVE'),
    u"Charges incluses": ('CHARGES', 'INCLUDED'),
    u"Charges selon consommation": ('CHARGES', 'ACCORDING_TO_CONSUMPTION'),
    u"Déduction si pas de petit déjeuner": ('', ''),
    u"Garantie": ('OTHER', 'GUARANTEE'),
    u"Haute saison - (Mid-week)": ('', ''),
    u"Haute saison - (Semaine)": ('HIGH_SEASON', 'WEEK'),
    u"Haute saison - (Week-end)": ('HIGH_SEASON', 'WEEKEND'),
    u"Moyenne saison - (Mid-week)": ('', ''),
    u"Moyenne saison - (Semaine)": ('MEDIUM_SEASON', 'WEEK'),
    u"Moyenne saison - (Week-end)": ('MEDIUM_SEASON', 'WEEKEND'),
    u"Nettoyage": ('', ''),
    u"Nettoyage inclus dans le montant de la location": ('', ''),
    u"Nettoyage par le locataire ou ....€": ('', ''),
    u"Réduction enfant / nuitée": ('', ''),
    u"Réduction enfant / repas": ('', ''),
    u"Semaine de fin année (Noël/Nouvel An)": ('OTHER', 'END_OF_YEAR'),
    u"Supplément 1 repas / personne / nuit": ('', ''),
    u"Supplément enfant / personne / nuit": ('', ''),
    u"Supplément table d'hôtes": ('OTHER', 'TABLES_HOTES'),
    u"Tarif spécial": ('', ''),
    u"Taxe de séjour € / jour / personne": ('OTHER', 'SOJOURN_TAX'),
    u"Week-end de fête": ('', ''),
    u"Week-end de fête / 3 nuits": ('FEAST_WEEKEND', '3_NIGHTS'),
    u"Week-end de fête / 4 nuits": ('FEAST_WEEKEND', '4_NIGHTS'),
}

"""
# LOW_SEASON	WEEK	t	f
# LOW_SEASON	WEEKEND	t	f
# MEDIUM_SEASON	WEEK	t	f
# MEDIUM_SEASON	WEEKEND	t	f
# HIGH_SEASON	WEEK	t	f
# HIGH_SEASON	WEEKEND	t	f
# FEAST_WEEKEND	3_NIGHTS	t	f
# FEAST_WEEKEND	4_NIGHTS	t	f
# CHARGES	ACCORDING_TO_CONSUMPTION	t	f
# CHARGES	INCLUDED	t	f
# CHARGES	INCLUSIVE	t	f
# ROOM	1_PERSON	f	t
# ROOM	2_PERSONS	f	t
ROOM	PERSON_SUP	f	t
# OTHER	END_OF_YEAR	t	t
# OTHER	GUARANTEE	t	t
OTHER	OTHER	t	t
# OTHER	SOJOURN_TAX	t	t
OTHER	WITHOUT_BREAKFAST	t	t
OTHER	TABLE_HOTES	t	t
"""


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
        changes.extend(self.compareProprios() or [])
        for change in changes:
            for diff in change['diff']:
                attr, obj1, obj2 = diff
                if self.origin == 'PIVOT':
                    old = obj1
                    new = obj2
                elif self.origin == 'GDW':
                    old = obj2
                    new = obj1
                if not self.notifDeniedExists(change['table'],
                                              change['pk'],
                                              new,
                                              attr):
                    self.insertNotification(change['table'],
                                            change['pk'],
                                            old,
                                            new,
                                            attr)
            self.pg_session.commit()
        self.pg_session.close()

    def notifDeniedExists(self, table, pk, new_value, attr):
        query = self.pg_session.query(Notification)
        query = query.filter(Notification.origin == self.origin)
        query = query.filter(Notification.table == table)
        query = query.filter(Notification.column == attr)
        query = query.filter(Notification.table_pk == str(pk))
        query = query.filter(Notification.new_value == unicode(new_value))
        query = query.filter(Notification.treated == False)  # noqa Disable pep8 E712
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
                diff = []
                # COMMUNE
                pivot_commune = get_best_match(self.pg_session, pivot_heb, Commune, COMCOLUMNS)
                diff.extend(get_differences(gdw_heb.commune, pivot_commune, ['com_pk']))

                # PROVINCE
                pivot_province = get_best_match(self.pg_session, pivot_heb, Province, PROVCOLUMNS)
                gdw_province = None
                if gdw_heb.province:
                    gdw_province = gdw_heb.province[0]
                diff.extend(get_differences(gdw_province, pivot_province, ['prov_pk']))

                # MAISON TOURISME
                pivot_tourisme = get_best_match(self.pg_session, pivot_heb, MaisonTourisme, MAISCOLUMNS)
                gdw_tourisme = None
                if gdw_heb.province:
                    gdw_tourisme = gdw_heb.maisonTourisme[0]
                diff.extend(get_differences(gdw_tourisme, pivot_tourisme, ['mais_pk']))

                # HEBERGEMENT
                diff.extend(get_differences(gdw_heb, pivot_heb, HEBCOLUMNS))

                result.append({'table': 'hebergement',
                               'pk': str(gdw_heb.heb_pk),
                               'diff': diff})
        return result

    def potentialProprio(self, proprio):
        result = []
        if self.origin == 'PIVOT':
            code_cgt = proprio.code_interne_CGT
            query = self.pg_session.query(Hebergement)
            query = query.filter(Hebergement.heb_code_cgt == code_cgt)
            heb = query.first()
            if heb:
                result.append(heb.proprio)
        elif self.origin == 'GDW':
            hebs = proprio.hebergements
            for heb in hebs:
                query = self.mysql_session.query(ContactView)
                query = query.filter(ContactView.code_interne_CGT == heb.heb_code_cgt)
                contact = query.first()
                if contact:
                    result.append(contact)
        return result

    def compareProprios(self):
        origin_changes = self.getLastPropriosChanges()
        result = []
        for origin_change in origin_changes:
            for proprio in self.potentialProprio(origin_change):
                diff = []
                if self.origin == 'PIVOT':
                    gdw_proprio = proprio
                    pivot_contact = origin_change
                elif self.origin == 'GDW':
                    gdw_proprio = origin_change
                    pivot_contact = proprio

                # PROPRIO
                diff.extend(get_differences(gdw_proprio, pivot_contact, PROCOLUMNS))

                # PROPRIO CIVILITE
                pivot_civilite = get_best_match(self.pg_session, pivot_contact, Civilite, CIVCOLUMNS)
                diff.extend(get_differences(gdw_proprio.civilite, pivot_civilite, ['civ_pk']))

                # PROPRIO COMMUNE
                pivot_commune = get_best_match(self.pg_session, pivot_contact, Commune, COMCOLUMNS)
                diff.extend(get_differences(gdw_proprio.commune, pivot_commune, ['com_pk']))

                result.append({'table': 'proprio',
                               'pk': str(gdw_proprio.pro_pk),
                               'diff': diff})
        return result

    def compareTarifs(self):
        """
        Compare tarifs between pivot and gites_wallons databases
        First get the last tarifs changes from the origin database
        Then compare with the destination database if the data is different
        Must be the same type, subtype, and heb
        pivot_tarif:
            code_cgt: GRNA1153 Basse saison - (Semaine) 200
        gdw_tarif:
            heb_pk: 81 LOW_SEASON WEEK 100

        return [{'table': 'tarifs',
                 'pk': tarif.pk,
                 'diff': [('min', 100, 110),
                          ('max', 200, 210)]},
                {'table': 'tarifs',
                 'pk': tarif.pk,
                 'diff': [('min', 50, 55),
                          ('cmt', 'foo', 'bar')]}]
        """
        origin_changes = self.getLastTarifsChanges()
        dest_hebergements = self.getHebergementsByCodeCgt([i.heb_code_cgt for i in origin_changes])
        result = []
        for origin_change in origin_changes:
            dest_heb = dest_hebergements[origin_change.heb_code_cgt]

            comparisons = []
            if self.origin == 'PIVOT':
                gdw_tarifs = Tarifs.get_hebergement_tarifs(heb_pk=dest_heb.heb_pk, session=self.pg_session)
                pivot_tarif = origin_change
                comparisons = self.get_tarifs_comparisons_pivot(gdw_tarifs, pivot_tarif)
            elif self.origin == 'GDW':
                gdw_tarif = origin_change
                pivot_tarifs = TarifView.get(heb_code_cgt=dest_heb.heb_code_cgt)
                comparisons = self.get_tarifs_comparisons_gdw(pivot_tarifs, gdw_tarif)

            result.extend(comparisons)

        return result

    def get_tarifs_comparisons_pivot(self, gdw_tarifs, pivot_tarif):
        """
        Get the differences for all lines

        gdw_tarifs = [gdw_tarif_1, gdw_tarif_2]
        gdw_tarif_1.type = LOW_SEASON
        gdw_tarif_1.subtype = WEEK
        gdw_tarif_1.min = 100
        gdw_tarif_1.max = 200
        gdw_tarif_1.cmt = null

        gdw_tarif_2.type = HIGH_SEASON
        gdw_tarif_2.subtype = WEEKEND
        gdw_tarif_2.min = 50
        gdw_tarif_2.max = 80
        gdw_tarif_2.cmt = null

        pivot_tarif.type = 'Basse saison - (Semaine)'
        pivot_tarif.min = 110
        pivot_tarif.max = 210
        pivot_tarif.complement_info = null

        return [{'table': 'tarifs',
                'pk': gdw_tarif_1.pk,
                'diff': [('min', 100, 110),
                        ('max', 200, 210)]}]
        """
        comparisons = []
        for gdw_tarif in gdw_tarifs:
            if self._is_same_tarif_type(pivot_tarif, gdw_tarif):
                differences = get_differences(gdw_tarif, pivot_tarif, TARIFCOLUMNS)
                if differences:
                    comparisons.append({'table': 'tarifs',
                                        'pk': str(gdw_tarif.pk),
                                        'diff': differences})
        return comparisons

    def get_tarifs_comparisons_gdw(self, pivot_tarifs, gdw_tarif):
        comparisons = []
        for pivot_tarif in pivot_tarifs:
            if self._is_same_tarif_type(pivot_tarif, gdw_tarif):
                differences = get_differences(gdw_tarif, pivot_tarif, TARIFCOLUMNS)
                if differences:
                    comparisons.append({'table': 'tarifs',
                                        'pk': str(gdw_tarif.pk),
                                        'diff': differences})
        return comparisons

    def _is_same_tarif_type(self, pivot_tarif, gdw_tarif):
        """
        Check if the tarifs are same type, regarding the differences between the 2 DB
        """
        type, subtype = TARIF_TYPES_CORRESPONDANCE.get(pivot_tarif.type)
        if gdw_tarif.type == type and gdw_tarif.subtype == subtype:
            return True
        else:
            return False

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

    def getLastPropriosChanges(self):
        """
        Get last proprios changes in origin DB for hebs that are in the 2 databases
        """
        if self.origin == 'PIVOT':
            last_changes = ContactView.get()
        elif self.origin == 'GDW':
            last_changes = Proprio.get_last_changes(self.date, session=self.pg_session)
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
