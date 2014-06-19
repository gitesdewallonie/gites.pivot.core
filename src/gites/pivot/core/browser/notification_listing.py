# encoding: utf-8
"""
gites.pivot.core

Created by schminitz
Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""

import zope.interface
from five import grok

from gites.db.content import NotificationOrigin
from gites.pivot.core.table import notification_listing


class HebComparisonView(grok.View):
    grok.context(zope.interface.Interface)
    grok.name(u'notification-listing')
    grok.require('zope2.View')
    grok.template('notification_listing')

    def get_table(self):
        """ Returns the render of the table """
        table = notification_listing.NotificationListingTable(
            self.context,
            self.request)
        table.update()
        return table.render()

    def get_origins(self):
        """ Return available origins to filter on """
        return NotificationOrigin.get()
