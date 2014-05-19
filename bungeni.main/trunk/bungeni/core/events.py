# Bungeni Parliamentary Information System - http://www.bungeni.org/
# Copyright (C) 2010 - Africa i-Parliaments - http://www.parliaments.info/
# Licensed under GNU GPL v2 - http://www.gnu.org/licenses/gpl-2.0.txt

""" Event handlers for various changes to objects

note that other events are handled in workflows
audit and files!

$Id$
"""
log = __import__("logging").getLogger("bungeni.core.events")


import datetime

from zope.security.proxy import removeSecurityProxy
from zope.lifecycleevent import IObjectModifiedEvent

from bungeni.alchemist import Session
from bungeni.models import domain
from bungeni.models.interfaces import (
    IGroupMember, 
    IMemberRole,
    ILegislativeContent,
)
from bungeni.utils import register


@register.handler(adapts=(IGroupMember, IObjectModifiedEvent))
def group_member_modified(ob, event):
    """when a group member gets inactivated (end date set)
    all his titles get deactivated for the same date (if they
    do not have an end date already
    """
    if ob.end_date:
        session = Session()
        trusted = removeSecurityProxy(ob)
        member_id = trusted.member_id
        titles = session.query(domain.MemberTitle).filter(
            domain.MemberTitle.member_id == member_id)
        for title in titles.all():
            if title.end_date == None:
                title.end_date = ob.end_date


@register.handler(adapts=(ILegislativeContent, IObjectModifiedEvent))
def timestamp(ob, event):
    """Set the timestamp for the item.
    """
    # !+ADD_SUB_OBJECT_MODIFIES_HEAD(mr, oct-2012) adding an event/attachment 
    # causes an ObjectMofiedEvent on head doc to be caught here... thus
    # updating its timestamp. Is this the desired behaviour?
    removeSecurityProxy(ob).timestamp = datetime.datetime.now()


