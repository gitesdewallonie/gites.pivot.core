# -*- coding: utf-8 -*-
"""
gites.pivot.core

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.viewlet.interfaces import IViewletManager


class INotificationListingTable(Interface):
    """ Marker interface for the notification listing table """
