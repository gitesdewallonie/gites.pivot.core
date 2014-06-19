# encoding: utf-8
"""
gites.pivot.core

Created by francois
Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""
from datetime import datetime
from gites.pivot.core import testing
from gites.pivot.core.scripts.changes import PivotChanges


class TestChanges(testing.PivotDBTestCase):
    pivot_sql_file = ('toffres')

    def test_getHebergementsCGT(self):
        changes = PivotChanges(None)
        hebergements = changes.getHebergementsCGT()
        self.assertEqual(hebergements, ['1', '2'])

    def test_getLastChanges(self):
        date = datetime(2014, 6, 1, 0, 0)
        changes = PivotChanges(None)
        lastChanges = changes.getLastChanges(date)
        self.assertEqual(len(lastChanges), 1)
