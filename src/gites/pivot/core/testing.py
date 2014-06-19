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

PIVOT_CORE_RDB = PGScriptRDB(name='PIVOTCORERDB', bases=(PIVOT_RDB, ))


class PivotTestCase(BaseTestCase):
    pass


class PivotDBTestCase(DatabaseTestCase):
    databases = ('pivot', 'gite')
    layer = PIVOT_CORE_RDB

    @property
    def pivot_session(self):
        return getUtility(IDatabase, 'mysql').session

    @property
    def gite_session(self):
        return getUtility(IDatabase, 'postgres').session
