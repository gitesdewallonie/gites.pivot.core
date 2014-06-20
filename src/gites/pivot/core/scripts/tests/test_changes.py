# encoding: utf-8
"""
gites.pivot.core

Created by francois
Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""
from gites.pivot.core import testing
from gites.pivot.core.scripts.changes import PivotChanges


class TestChanges(testing.PivotDBTestCase):
    pivot_sql_file = ('toffres')
    gite_sql_file = ('hebergement')

    def test_getHebergementsCGT(self):
        args = type('args', (object, ), {'date': '2014/06/01'})()
        changes = PivotChanges(args)
        hebergements = changes.getHebergementsCGT()
        self.assertEqual(len(hebergements), 1)

    def test_getLastChanges(self):
        args = type('args', (object, ), {'date': '2014/06/01'})()
        changes = PivotChanges(args)
        lastChanges = changes.getLastChanges()
        self.assertEqual(len(lastChanges), 1)

    def test_compareGitesWithPivot(self):
        args = type('args', (object, ), {'date': '2014/06/01'})()
        changes = PivotChanges(args)
        differences = changes.compareGitesWithPivot()
        self.assertEqual(len(differences), 1)
        # heb_pk
        self.assertEqual(differences[0][0], '81')
        # tuple of diff
        self.assertEqual(len(differences[0][1]), 22)
