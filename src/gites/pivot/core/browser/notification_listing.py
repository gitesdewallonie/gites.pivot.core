# encoding: utf-8
"""
gites.pivot.core

Created by schminitz
Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""

import zope.interface
from plone import api
from five import grok

from gites.db.content import NotificationOrigin
from gites.pivot.core.table import notification_listing

from gites.db.content import (Notification,
                              Hebergement,
                              LinkHebergementMetadata,
                              Proprio,
                              Tarifs)


class HebComparisonView(grok.View):
    grok.context(zope.interface.Interface)
    grok.name(u'notification-listing')
    grok.require('gdw.ViewAdmin')
    grok.template('notification_listing')

    @property
    def origin(self):
        return self.request.get('origin', 'GDW')

    @property
    def status(self):
        return self.request.get('status', 'UNTREATED')

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

    def update(self):
        """ Treat notification selected by user in table """
        # Get selected radio buttons
        for key in self.request.form:
            if key.startswith('notif_'):
                pk = int(key.strip('notif_'))
                treated = self.request.form[key] == 'YES' and True or False

                notif = Notification.first(pk=pk)

                # Do not treat already treated notif
                if notif.treated:
                    return

                if notif.origin == 'PIVOT':
                    if treated:
                        self._apply_pivot_notif(notif)
                    self._treat_notification(notif, treated)
                elif notif.origin == 'GDW':
                    self._treat_notification(notif, treated)

    def _apply_pivot_notif(self, notif):
        line = self._get_line(notif.table, notif.table_pk)
        setattr(line, notif.column, notif.new_value)
        line.save()

    def _get_line(self, table_name, table_pk):
        mappers = {'hebergement': (Hebergement, 'heb_pk'),
                   'proprio': (Proprio, 'pro_pk'),
                   'link_hebergement_metadata': (LinkHebergementMetadata, 'link_met_pk'),
                   'tarifs': (Tarifs, 'pk')}

        table, column = mappers[table_name]
        return table.first(**{column: table_pk})

    def _treat_notification(self, notif, treated):
        """
        Set notification to treated
        """
        notif.treat(treated=treated, user=api.user.get_current().id)
