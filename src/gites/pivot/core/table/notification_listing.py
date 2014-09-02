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
from gites.db.content import (LinkHebergementMetadata,
                              Metadata,
                              Tarifs)
from itertools import cycle
from plone.z3ctable.batch import BatchProvider
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest
from ZTUtils import url_query, make_query

BATCHSIZE = 30
STARTBATCHINGAT = 0


class NotificationBatchProvider(BatchProvider, grok.MultiAdapter):
    grok.adapts(Interface, IBrowserRequest, interfaces.INotificationListingTable)
    grok.name('notificationbatch')

    def makeUrl(self, index):
        batch = self.batches[index]
        baseQuery = dict(self.request.form)
        query = {self.table.prefix + '-batchStart': batch.start,
                 self.table.prefix + '-batchSize': batch.size}
        baseQuery.update(query)
        querystring = make_query(baseQuery)
        base = url_query(self.request, omit=baseQuery.keys())
        return '%s&%s' % (base, querystring)


class NotificationListingTable(table.SequenceTable):
    zope.interface.implements(interfaces.INotificationListingTable)

    # Defines if the table must be rendered if there's no values
    render_none = False
    cssClasses = {'table': 'z3c-listing percent100 listing notification-listing'}
    cssClassEven = u'odd'
    cssClassOdd = u'even'
    sortOn = None
    batchSize = BATCHSIZE
    startBatchingAt = STARTBATCHINGAT

    @property
    def values(self):
        """ Returns the values for an hosting """
        adapter = zope.component.getMultiAdapter(
            (self.context, self.request, self), table_interfaces.IValues)
        return adapter.values

    def update(self):
        """
        Override method for update from SequenceTable that adds a
        batchProvideAdapter before the update
        """
        self.batchProviderName = 'notificationbatch'
        table.SequenceTable.update(self)

    def render(self):
        """ Overrides of the render method from SequenceTable """
        if not len(self.rows) and self.render_none is False:
            return None
        return "%s%s%s" % (
            self.renderBatch(),
            super(table.SequenceTable, self).render(),
            self.renderBatch())

    def setUpRows(self):
        values, self.length = self.values
        rows = [self.setUpRow(item) for item in values]
        rowsCycle = CycleList(rows)
        rowsCycle.length = self.length
        return rowsCycle

    def renderRows(self):
        """
        Override of the default methods to group by table pk
        """
        counter = 0
        rows = []
        cssClasses = (self.cssClassEven, self.cssClassOdd)
        append = rows.append
        pk = ''
        for row in self.rows:
            cssClass = ''
            if pk != row[0][0].table_pk:
                pk = row[0][0].table_pk
                cssClass = 'line '
                counter += 1
            cssClass = '%s%s' % (cssClass, cssClasses[counter % 2])
            append(self.renderRow(row, cssClass))
        return u''.join(rows)


class CycleList(cycle):
    """
    simulate a list with a cycle iterable
    You have to define the length of the simulated list
    foo = CycleList()
    foo.length = myLength
    """

    length = 0

    def __getitem__(self, number):
        if isinstance(number, int):
            for i in range(BATCHSIZE):
                if i == number:
                    item = self.next()
                else:
                    self.next()
            return item

        elif isinstance(number, slice):
            start = number.start or 0
            stop = number.stop or BATCHSIZE
            itemList = []
            rangeOfSlice = range(start, stop)
            for i in range(BATCHSIZE + start):
                if i in rangeOfSlice:
                    itemList.append(self.next())
                else:
                    self.next()
            return itemList
        else:
            errorMessage = """CycleList indices must be integers, not %s""" % \
                type(number).__name__
            raise TypeError(errorMessage)

    def __len__(self):
        return self.length


class NotificationListingValues(value.ValuesMixin,
                                grok.MultiAdapter):
    grok.provides(table_interfaces.IValues)
    grok.adapts(zope.interface.Interface,
                zope.publisher.interfaces.browser.IBrowserRequest,
                interfaces.INotificationListingTable)

    @property
    def values(self):
        status = self.request.get('status', 'UNTREATED')
        origin = self.request.get('origin', 'GDW')

        if status == 'UNTREATED':
            values = Notification.get_untreated_notifications(origin)
        else:
            values = Notification.get_treated_notifications(origin)
        return self.mappingNotification(values), len(values)

    def mappingNotification(self, values):
        listing = []
        for notif in values:
            table_pk = notif.table_pk
            column = notif.column
            if notif.table == 'link_hebergement_metadata':
                link = LinkHebergementMetadata.first(link_met_pk=notif.table_pk)
                meta = Metadata.first(met_pk=link.metadata_fk)
                table_pk = '%s (Heb: %s)' % (notif.table_pk, link.heb_fk)
                column = '%s (%s)' % (notif.column, meta.met_titre_fr)
            elif notif.table == 'tarifs':
                tarif = Tarifs.first(pk=notif.table_pk)
                table_pk = "%s (Heb: %s)" % (notif.table_pk, tarif.heb_pk)
                column = "%s (%s/%s)" % (notif.column, tarif.type, tarif.subtype)
            listing.append(type('obj', (object,), {'pk': notif.pk,
                                                   'origin': notif.origin,
                                                   'table': notif.table,
                                                   'column': column,
                                                   'table_pk': table_pk,
                                                   'old_value': notif.old_value,
                                                   'new_value': notif.new_value,
                                                   'date': notif.date,
                                                   'treated': notif.treated,
                                                   'cmt': notif.cmt,
                                                   'user': notif.user}))
        return listing


class NotificationListingColumn(column.GetAttrColumn):
    """ Base class for the comparison columns """
    grok.provides(table_interfaces.IColumn)
    grok.adapts(zope.interface.Interface,
                zope.interface.Interface,
                interfaces.INotificationListingTable)


class NotificationListingColumnOrigin(NotificationListingColumn, grok.MultiAdapter):
    grok.name('origin')
    header = u'Origine'
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


class NotificationListingColumnDate(NotificationListingColumn, grok.MultiAdapter):
    grok.name('date')
    header = u'Date'
    weight = 70

    def renderCell(self, item):
        return getattr(item, 'date').strftime('%d-%m-%Y')


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
        origin = self.request.get('origin', 'GDW')
        status = self.request.get('status', 'UNTREATED')

        if status == 'UNTREATED':
            if origin == "GDW":
                yes = u'Traité'
                no = u'Ignorer'
            elif origin == "PIVOT":
                yes = u'Accepter'
                no = u'Refuser'

            render = u'''
                {0[yes]}: <input type="radio" name="notif_{0[pk]}" value="YES" />
                {0[no]}: <input type="radio" name="notif_{0[pk]}" value="NO" />
                '''.format({'yes': yes,
                            'no': no,
                            'pk': item.pk})
        else:
            if origin == "GDW":
                yes = u'Traité'
                no = u'Ignoré'
            elif origin == "PIVOT":
                yes = u'Accepté'
                no = u'Refusé'
            render = item.treated and yes or no
        return render
