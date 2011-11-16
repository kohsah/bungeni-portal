# Bungeni Parliamentary Information System - http://www.bungeni.org/
# Copyright (C) 2010 - Africa i-Parliaments - http://www.parliaments.info/
# Licensed under GNU GPL v2 - http://www.gnu.org/licenses/gpl-2.0.txt

"""Auditing of Changes for Domain Objects

$Id$
"""
log = __import__("logging").getLogger("bungeni.core.audit")


__all__ = ["get_auditor", "set_auditor"]


from datetime import datetime
from types import StringTypes

from zope.lifecycleevent import IObjectModifiedEvent, IObjectCreatedEvent, \
    IObjectRemovedEvent
    
from zope.annotation.interfaces import IAnnotations
from zope.security.proxy import removeSecurityProxy
from zope import lifecycleevent

from sqlalchemy import orm
from bungeni.alchemist import Session
from bungeni.alchemist.interfaces import IRelationChange

from bungeni.models.utils import get_db_user_id
from bungeni.models.interfaces import IAuditable
from bungeni.models import schema
from bungeni.models import domain
from bungeni.core.workflow.interfaces import IWorkflow, IWorkflowTransitionEvent
from bungeni.core.interfaces import IVersionCreated, IVersionReverted
from bungeni.ui.utils import common
from bungeni.utils import register

from bungeni.core.i18n import _


def _trace_audit_handler(ah):
    def _ah(ob, event):
        log.debug("CALLING audit.%s(%s, %s)" % (ah.__name__, ob, event))
        ah(ob, event)
    return _ah


# change handlers

@register.handler(adapts=(IAuditable, IObjectCreatedEvent))
@_trace_audit_handler
def _object_added(ob, event):
    auditor = get_auditor(ob)
    auditor.object_added(removeSecurityProxy(ob), event)

@register.handler(adapts=(IAuditable, IObjectModifiedEvent))
@_trace_audit_handler
def _object_modified(ob, event):
    # !+CHECK_CHANGE_ID(mr, nov-2011) why was this check here in the first 
    # place? The change db record is ALWAYS yet to be created at this point?!?
    #try:
    #    assert getattr(event, "change_id", None) is not None, \
    #        "ObjectModified -> no change_id!"
    #except AssertionError, e:
    #    # !+CHANGE_ID(mr, nov-2011) change_id is sometimes not yet defined
    #    log.warn(" *** %s: IGNORING EVENT %s FOR %s" % (e, event, ob))
    #    return
    auditor = get_auditor(ob)
    auditor.object_modified(removeSecurityProxy(ob), event)

@register.handler(adapts=(IAuditable, IObjectRemovedEvent))
@_trace_audit_handler
def _object_removed(ob, event):
    auditor = get_auditor(ob)
    auditor.object_removed(removeSecurityProxy(ob), event)

@register.handler(adapts=(IAuditable, IWorkflowTransitionEvent))
@_trace_audit_handler
def _object_transitioned(ob, event):
    auditor = get_auditor(ob)
    change_id = auditor.object_transitioned(removeSecurityProxy(ob), event)
    event.change_id = change_id

# !+CHANGELOG_DATA_DUPLICATION(mr, nov-2011)
@register.handler(adapts=(IAuditable, IVersionCreated))
@_trace_audit_handler
def _object_versioned(ob, event):
    """When an auditable object is versioned, we audit creation of new version.
    """
    auditor = get_auditor(ob)
    change_id = auditor.object_versioned(removeSecurityProxy(ob), event)
    event.version.change_id = change_id

# !+CHANGELOG_DATA_DUPLICATION(mr, nov-2011) possibly...
@register.handler(adapts=(IAuditable, IVersionReverted))
@_trace_audit_handler
def _object_version_reverted(ob, event):
    auditor = get_auditor(ob)
    change_id = auditor.object_version_reverted(removeSecurityProxy(ob), event)
    event.change_id = change_id


# utilities 

# !+CHANGELOG_DATA_DUPLICATION(mr, nov-2011) attachment/signatory added/modified 
# are already logged on the items themselves--changelogging these also on the 
# parent object is essentially data duplication. 
#
# Clients of change information e.g. the timeline, should simply "aggregate" 
# changes e.g. changes on head doc + changes on atttached + etc.

@_trace_audit_handler
def object_attachment(ob, event):
    """Utility to log--on the parent object--changes on one of its attachments.
    event.action: "added", "modified"
    """
    auditable_parent = _get_auditable_ancestor(ob)
    # !+attachment_added(mr, nov-2011) auditable_parent is always None on "added"?
    if auditable_parent:
        event.description = "File attachment %s %s %s" % (
            ob.file_title, ob.file_name, event.action)
        get_auditor(auditable_parent).object_attachment(auditable_parent, event)

@_trace_audit_handler
def object_signatory(ob, event):
    """Utility to log--on the parent object--changes on one of its signatories.
    event.action: "added", "modified"
    """
    auditable_parent = ob.item
    auditor = get_auditor(auditable_parent) 
    auditor.object_signatory(auditable_parent, event)


# internal utilities

def _get_auditable_ancestor(obj):
    parent = obj.__parent__
    while parent:
        if  IAuditable.providedBy(parent):
            return parent
        else:
            parent = getattr(parent, "__parent__", None)

class _AuditorFactory(object):
    
    def __init__(self, change_table, change_class):
        self.change_table = change_table
        self.change_class = change_class
    
    # handlers, return the change_id
    
    # Called directly from signatory added/modified handlers
    def object_signatory(self, ob, event):
        return self._object_changed(event.action, ob, event.description)
    
    # Called directly from attachment added/modified handlers
    def object_attachment(self, ob, event):
        # !+ this makes no distinction between added/modified changes anyway?!
        return self._object_changed("attachment", ob, event.description)
    
    def object_added(self, ob, event):
        return self._object_changed("added", ob)
    
    def object_modified(self, ob, event):
        attrset = []
        for attr in event.descriptions:
            if lifecycleevent.IAttributes.providedBy(attr):
                attrset.extend(
                    [ attr.interface[a].title for a in attr.attributes ]
                )
            elif IRelationChange.providedBy(attr):
                if attr.description:
                    attrset.append(attr.description)
        attrset.append(getattr(ob, "note", ""))
        str_attrset = []
        for a in attrset:
            if type(a) in StringTypes:
                str_attrset.append(a)
        description = u", ".join(str_attrset)
        change_data = self._get_change_data()
        if change_data["note"]:
            extras = {"comment": change_data["note"]}
        else:
            extras = None
        return self._object_changed("modified", ob, 
                        description=description,
                        extras=extras,
                        date_active=change_data["date_active"])
    
    def object_transitioned(self, ob, event):
        """
        ob: origin domain workflowed object 
        event: bungeni.core.workflow.states.WorkflowTransitionEvent
            .object # origin domain workflowed object 
            .source # source state
            .destination # destination state
            .transition # transition
            .comment #
        """
        change_data = self._get_change_data()
        # if note, attach it on object (if object supports such an attribute)
        if change_data["note"]:
            if hasattr(ob, "note"):
                ob.note = change_data["note"]
        # update object's workflow status date (if supported by object)
        if hasattr(ob, "status_date"):
            ob.status_date = change_data["date_active"] or datetime.now()
        # as a "base" description, use human readable workflow state title
        wf = IWorkflow(ob) # !+ adapters.get_workflow(ob)
        description = wf.get_state(event.destination).title
        # extras, that may be used e.g. to elaborate description at runtime
        extras = {
            "source": event.source, 
            "destination": event.destination,
            "transition": event.transition.id,
            "comment": change_data["note"]
        }
        return self._object_changed("workflow", ob, 
                        description=description,
                        extras=extras,
                        date_active=change_data["date_active"])
        # description field is a "building block" for a UI description;
        # extras/notes field becomes interpolation data
    
    def object_removed(self, ob, event):
        #return self._object_changed("deleted", ob)
        return

    def object_versioned(self, ob, event):
        """
        ob: origin domain workflowed object 
        event: bungeni.core.interfaces.VersionCreated
            .object # origin domain workflowed object 
            .message # title of the version object
            .version # bungeni.models.domain.*Version
            .versioned # bungeni.core.version.Versioned
        """
        session = Session()
        session.add(event.version)

        # !+version_id At this point, new version instance (at event.version) is not yet 
        # persisted to the db (or added to the session!) so its version_id is
        # still None. We force the issue, by adding it to session and flushing.
        session.flush()
        # as base description, record a the version object's title
        description = event.message
        # extras, that may be used e.g. to elaborate description at runtime        
        extras = {
            "version_id": event.version.version_id # !+version_id
        }
        return self._object_changed("new-version", ob, description, extras)
        #vkls = getattr(domain, "%sVersion" % (ob.__class__.__name__))
        #versions = session.query(vkls
        #            ).filter(vkls.content_id==event.version.content_id
        #            ).order_by(vkls.status_date).all()

    def object_version_reverted(self, ob, event):
        return self._object_changed("reverted-version", ob,
            description=event.message)
    
    #
    
    def _object_changed(self, change_kind, ob, 
            description="", extras=None, date_active=None):
        """
        description: 
            this is a non-localized string as base description of the log item,
            offers a (building block) for the description of this log item. 
            UI components may use this in any of the following ways:
            - AS IS, optionally localized
            - as a building block for an elaborated description e.g. for 
              generating descriptions that are hyperlinks to an event or 
              version objects
            - ignore it entirely, and generate a custom description via other
              means e.g. from the "notes" extras dict.
        
        extras: !+CHANGE_EXTRAS(mr, dec-2010)
            a python dict, containing "extra" information about the log item, 
            with the "key/value" entries depending on the change "action"; 

            Specific examples, for actions: 
                workflow: self.object_transitioned()
                    source
                    destination
                    transition
                    comment
                new-version: self.object_versioned()
                    version_id
                modified: self.object_modified()
                    comment
            
            For now, this dict is serialized (using repr(), values are assumed 
            to be simple strings or numbers) as the value of the notes column, 
            for storing in the db--but if and when the big picture of these 
            extra keys is understood clearly then the changes table may be 
            redesigned to accomodate for a selection of these keys as real 
            table columns.                        
        
        date_active:
            the UI for some changes allow the user to manually set the 
            date_active -- this is what should be used as the *effective* date 
            i.e. the date to be used for all intents and purposes other than 
            for data auditing. When not user-modified, the value should be equal 
            to date_audit. 
        """
        oid, otype = self._getKey(ob)
        user_id = get_db_user_id()
        assert user_id is not None, _("Audit error. No user logged in.")
        session = Session()
        change = self.change_class()
        change.action = change_kind
        change.date_audit = datetime.now()
        if date_active:
            change.date_active = date_active
        else:
            change.date_active = change.date_audit
        change.user_id = user_id
        change.description = description
        change.extras = extras
        change.content_type = otype
        change.head = ob # attach change to parent object
        change.status = ob.status # remember parent's status at time of change
        session.add(change)
        session.flush()
        log.debug("AUDITED CHANGE [%s] %s" % (change_kind, change.__dict__))
        return change.change_id
    
    #
    
    def _getKey(self, ob):
        mapper = orm.object_mapper(ob)
        primary_key = mapper.primary_key_from_instance(ob)[0]
        return primary_key, unicode(ob.__class__.__name__)

    def _get_change_data(self):
        """If request defines change_data, use it, else return a dummy dict.
        """
        try:
            cd = IAnnotations(common.get_request()).get("change_data")
            assert cd is not None, "change_data dict is None."
        except (TypeError, AssertionError):
            # Could not adapt... under testing, the "request" is a 
            # participation that has no IAnnotations.
            cd = {}
        cd.setdefault("note", cd.get("note", ""))
        cd.setdefault("date_active", cd.get("date_active", None))
        return cd


# module-level dedicated auditor singleton instance per auditable class

def get_auditor(ob):
    """Get the module-level dedicated auditor singleton instance for the 
    auditable ob.__class__ -- raise KeyError if no such auditor singleton.
    """
    return globals()["%sAuditor" % (ob.__class__.__name__)]

def set_auditor(kls):
    """Set the module-level dedicated auditor singleton instance for the 
    auditable kls.
    """
    name = kls.__name__
    auditor_name = "%sAuditor" % (name)
    log.debug("Setting AUDITOR %s [for type %s]" % (auditor_name, name))
    change_kls = getattr(domain, "%sChange" % (name))
    change_tbl = getattr(schema, "%s_changes" % (schema.un_camel(name)))
    globals()[auditor_name] = _AuditorFactory(change_tbl, change_kls)

for kls in domain.CUSTOM_DECORATED["auditable"]:
    set_auditor(kls)
    
#

