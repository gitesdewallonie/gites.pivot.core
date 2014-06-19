# encoding: utf-8
"""
gites.pivot.core

Created by schminitz
Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""

import zope.component
import zope.interface
import zope.publisher
from five import grok

from z3c.table import column, interfaces as table_interfaces, table, value

from gites.pivot.core import interfaces
from gites.db.content.notification import Notification


class NotificationListingTable(table.Table):
    zope.interface.implements(interfaces.INotificationListingTable)

    cssClasses = {'table': 'z3c-listing percent100 listing nosort comparison'}
    cssClassEven = u'odd'
    cssClassOdd = u'even'
    sortOn = None
    startBatchingAt = 30

    @property
    def values(self):
        """ Returns the values for an hosting """
        adapter = zope.component.getMultiAdapter(
            (self.context, self.request, self), table_interfaces.IValues)
        return adapter.values


class NotificationListingValues(value.ValuesMixin,
                                grok.MultiAdapter):
    grok.provides(table_interfaces.IValues)
    grok.adapts(zope.interface.Interface,
                zope.publisher.interfaces.browser.IBrowserRequest,
                interfaces.INotificationListingTable)

    @property
    def values(self):
        origin = self.request.get('origin', 'GDW')

        values = Notification.get_untreated_notifications(origin)
        return values


class NotificationListingColumn(column.GetAttrColumn):
    """ Base class for the comparison columns """
    grok.provides(table_interfaces.IColumn)
    grok.adapts(zope.interface.Interface,
                zope.interface.Interface,
                interfaces.INotificationListingTable)


class NotificationListingColumnOrigin(NotificationListingColumn, grok.MultiAdapter):
    grok.name('origin')
    header = u'origin'
    attrName = u'origin'
    weight = 10


class NotificationListingColumnTable(NotificationListingColumn, grok.MultiAdapter):
    grok.name('table')
    header = u'Table'
    attrName = u'table'
    weight = 20


class NotificationListingColumnColumn(NotificationListingColumn, grok.MultiAdapter):
    grok.name('column')
    header = u'Colonne'
    attrName = u'column'
    weight = 30


class NotificationListingColumnTablePk(NotificationListingColumn, grok.MultiAdapter):
    grok.name('table_pk')
    header = u'Table pk'
    attrName = u'table_pk'
    weight = 40


class NotificationListingColumnOldValue(NotificationListingColumn, grok.MultiAdapter):
    grok.name('old_value')
    header = u'Ancienne valeur'
    attrName = u'old_value'
    weight = 50


class NotificationListingColumnNewValue(NotificationListingColumn, grok.MultiAdapter):
    grok.name('new_value')
    header = u'Nouvelle valeur'
    attrName = u'new_value'
    weight = 60


class NotificationListingColumnCmt(NotificationListingColumn, grok.MultiAdapter):
    grok.name('cmt')
    header = u'Commentaire'
    weight = 80

    def renderCell(self, item):
        return getattr(item, 'cmt') or ''


class NotificationListingColumnTreated(NotificationListingColumn, grok.MultiAdapter):
    grok.name('treated')
    attrName = u'treated'
    weight = 90

    @property
    def header(self):
        origin = self.request.get('origin', 'GDW')
        header = origin == 'GDW' and u'Traité' or u'Appliquer'
        return header

    def renderCell(self, item):
        return u'''
                Oui: <input type="radio" name="notif_{0[pk]}" value="YES" />
                Non: <input type="radio" name="notif_{0[pk]}" value="NO" />
                '''.format({'pk': item.pk})
