# encoding: utf-8
"""
gites.pivot.core

Created by mpeeters
Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""

from affinitic.db.interfaces import IDatabase
from affinitic.testing import DatabaseTestCase
from affinitic.testing import BaseTestCase
from gites.pivot.db.testing import PIVOT_RDB
from zope.component import getUtility
from gites.db.testing import PGScriptRDB

PIVOTCORERDB = PGScriptRDB(name='PIVOTCORERDB', bases=(PIVOT_RDB, ))


class PivotTestCase(BaseTestCase):
    pass


class PivotDBTestCase(DatabaseTestCase):
    databases = ('pivot', )
    layer = PIVOTCORERDB

    @property
    def pivot_session(self):
        return getUtility(IDatabase, 'mysql').session
