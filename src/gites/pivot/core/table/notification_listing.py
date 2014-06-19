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
        origin = self.request.get('origin', None)

        gdw = type('obj', (object, ), {'name': 'gdw'})()
        pivot = type('obj', (object, ), {'name': 'pivot'})()

        if origin is None or origin == 'GDW':
            return [gdw]
        elif origin == 'PIVOT':
            return [pivot]
        else:
            return [gdw, pivot]


class NotificationListingColumn(column.GetAttrColumn):
    """ Base class for the comparison columns """
    grok.provides(table_interfaces.IColumn)
    grok.adapts(zope.interface.Interface,
                zope.interface.Interface,
                interfaces.INotificationListingTable)


class NotificationListingColumnName(NotificationListingColumn, grok.MultiAdapter):
    grok.name('name')
    header = u'Nom'
    attrName = u'name'
    weight = 10
