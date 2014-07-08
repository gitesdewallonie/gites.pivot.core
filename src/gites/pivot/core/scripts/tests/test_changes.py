# encoding: utf-8
"""
gites.pivot.core

Created by francois
Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""
from gites.pivot.core import testing
from gites.pivot.core.scripts.changes import PivotChanges
from gites.db.content import Notification


class TestChanges(testing.PivotDBTestCase):
    pivot_sql_file = ('toffres')
    gite_sql_file = ('changes')

    def test_notifDeniedExists(self):
        """
        Test notification already exists and denied
        """
        args = type('args', (object, ), {'date': '2014/06/01',
                                         'origin': 'PIVOT'})()
        changes = PivotChanges(args)
        exists = changes.notifDeniedExists('hebergement', '81', 'La Turbine 2', 'heb_nom')
        self.assertEqual(exists, 0)

        exists = changes.notifDeniedExists('hebergement', '81', 'Namur', 'heb_localite')
        self.assertEqual(exists, 1)

    def test_compareHebergementsPivot(self):
        args = type('args', (object, ), {'date': '2014/06/01',
                                         'origin': 'PIVOT'})()
        changes = PivotChanges(args)
        differences = changes.compareHebergements()
        self.assertEqual(len(differences), 1)
        self.assertEqual(differences[0]['pk'], '81')
        self.assertEqual(len(differences[0]['diff']), 22)
        changes.pg_session.close()

    def test_compareHebergementsGdw(self):
        return

    def test_compareTarifsPivot(self):
        args = type('args', (object, ), {'date': '2014/06/01',
                                         'origin': 'PIVOT'})()
        changes = PivotChanges(args)
        differences = changes.compareTarifs()
        self.assertEqual(len(differences), 1)
        self.assertEqual(differences[0]['pk'], '262')
        self.assertEqual(len(differences[0]['diff']), 2)
        changes.pg_session.close()

    def test_compareTarifsGdw(self):
        return


    def test_insertNotification(self):
        args = type('args', (object, ), {'date': '2014/06/01',
                                         'origin': 'PIVOT'})()
        changes = PivotChanges(args)
        changes.insertNotification('hebergement', '81', 'La Turbine', 'La Nouvelle Turbine', 'heb_nom')
        changes.pg_session.commit()
        notif = Notification.get(table_pk='81', new_value='La Nouvelle Turbine')
        self.assertEqual(len(notif), 1)
        changes.pg_session.close()

    def test_getHebergementsByCodeCgt(self):
        args = type('args', (object, ), {'date': '2014/06/01',
                                         'origin': 'PIVOT'})()
        changes = PivotChanges(args)

        hebergements = changes.getHebergementsByCodeCgt(('GRNA1153', ))
        self.assertEqual(len(hebergements), 1)

        hebergements = changes.getHebergementsByCodeCgt(('GRNA1153', 'GRNA5403'))
        self.assertEqual(len(hebergements), 2)

        changes.pg_session.close()

    def test_getLastHebergementsChanges(self):
        args = type('args', (object, ), {'date': '2014/06/01',
                                         'origin': 'PIVOT'})()
        changes = PivotChanges(args)
        lastChanges = changes.getLastHebergementsChanges()
        self.assertEqual(len(lastChanges), 1)
        changes.pg_session.close()

    def test_getLastHebergementsChangesGdw(self):
        args = type('args', (object, ), {'date': '2014/06/01',
                                         'origin': 'GDW'})()
        changes = PivotChanges(args)
        lastChanges = changes.getLastHebergementsChanges()
        self.assertEqual(len(lastChanges), 1)
        changes.pg_session.close()

    def test_getLastTarifsChanges(self):
        args = type('args', (object, ), {'date': '2014/06/01',
                                         'origin': 'PIVOT'})()
        changes = PivotChanges(args)
        lastChanges = changes.getLastTarifsChanges()
        self.assertEqual(len(lastChanges), 1)
        changes.pg_session.close()

    def test_getLastTarifsChangesGdw(self):
        args = type('args', (object, ), {'date': '2014/06/01',
                                         'origin': 'GDW'})()
        changes = PivotChanges(args)
        lastChanges = changes.getLastTarifsChanges()
        self.assertEqual(len(lastChanges), 1)
        changes.pg_session.close()
