#!/usr/bin/env python
# -*- coding: utf-8 -*-

# bungeni - http://www.bungeni.org/
# Parliamentary and Legislative Information System
# Copyright (C) 2010 UN/DESA - http://www.un.org/esa/desa/
# Licensed under GNU GPL v2 - http://www.gnu.org/licenses/gpl-2.0.txt

'''Utilities to help with working with queries on the domain model

$Id$
'''
log = __import__("logging").getLogger("bungeni.models.utils")
from zope import component
from zope.securitypolicy.interfaces import IPrincipalRoleMap
from zope.securitypolicy.settings import Allow, Deny
from zope.security.management import getInteraction
from zope.publisher.interfaces import IRequest
from ore.alchemist import Session
import sqlalchemy as rdb
from sqlalchemy import sql
from sqlalchemy.orm import eagerload, lazyload
import domain, schema

# !+ move "contextual" utils to ui.utils.contextual

def get_principal():
    """ () -> either(IPrincipal, None)
    """
    interaction = getInteraction()
    for participation in interaction.participations:
        if IRequest.providedBy(participation):
            return participation.principal
    
def get_principal_id():
    """ () -> either(str, None)
    """
    principal = get_principal()
    if principal is not None:
        return principal.id


def get_db_user(context=None):
    """ get the logged in user 
    Note: context is not used, but accommodated for as a dummy optional input 
    parameter to allow usage of this utility in e.g.
    bungeni.core.apps.py: container_getter(get_db_user, 'questions')
    """
    principal_id = get_principal_id()
    session = Session()
    query = session.query(domain.User).filter(domain.User.login==principal_id)
    results = query.all()
    if len(results)==1:
        return results[0]

def get_db_user_id(context=None):
    """ get the (numerical) user_id for the currently logged in user
    """
    db_user = get_db_user(context)
    if db_user is not None:
        return db_user.user_id

# contextual
def get_current_parliament(context):
    from bungeni.core import globalsettings
    return globalsettings.get_current_parliament()

def container_getter(getter, name, query_modifier=None):
    def func(context):
        obj = getter(context)
        try: 
            c = getattr(obj, name)
        except AttributeError:
            # the container we need is not there, data may be missing in the db
            from zope.publisher.interfaces import NotFound
            raise NotFound(context, name)
        c.setQueryModifier(sql.and_(c.getQueryModifier(), query_modifier))
        return c
    func.__name__ = "get_%s_container" % name
    return func

def get_container_by_role(context):
    """Determine container based on the contextual principal's roles
    
    parliament-level access:
        "bungeni.Clerk", "bungeni.Speaker", "bungeni.MP"
    ministry(ies)-level access:
        "bungeni.Minister"
    owner-level (user) access:
        "zope.Manager", "bungeni.Admin", , "bungeni.Owner", 
        "bungeni.Everybody", "bungeni.Anybody"
    
    """
    access_level = {'owner':True, 'ministry':False, 'parliament':False}
    
    # For sub-containers of Section instances, the context being passed is the 
    # Section instance itself -- but this is not the correct context to 
    # determine the user's roles in. Thus, workaround for this is to fallback
    # to the current parliament object if context passed is NOT a domain object.
    if not domain.object_hierarchy_type(context):
        log.debug("context %s for get_roles() is NOT a domain object, " 
            "falling back to current parliament as context" % context)
        roles = get_roles(get_current_parliament(None))
    else:
        roles = get_roles(context)
    
    for role_id in roles:
        if role_id in ("bungeni.Clerk", "bungeni.Speaker", "bungeni.MP"):
            access_level['parliament'] = True
        if role_id in ("bungeni.Minister",):
            access_level['ministry'] = True
    
    # get highest-privileged container
    if access_level['parliament']:
        return get_current_parliament(context)
    elif access_level['ministry']:
        # multi-ministry container
        return get_current_parliament(context)
    else:
        return get_db_user(context)

def get_roles(context):
    """Get contextual principal's roles
    
    return [ role_id for role_id, role 
             in component.getUtilitiesFor(IRole, context) ]
    eeks we have to loop through all groups of the principal and all 
    PrincipalRoleMaps to get all roles
    
    """
    prms = []
    def _build_principal_role_maps(ctx):
        if ctx is not None:
            if component.queryAdapter(ctx, IPrincipalRoleMap):  
                prms.append(IPrincipalRoleMap(ctx))
            _build_principal_role_maps(getattr(ctx,'__parent__', None))
    _build_principal_role_maps(context)
    prms.reverse()
    
    def add_roles(principal, prms, roles):
        for prm in prms:
            l_roles = prm.getRolesForPrincipal(principal) # -> generator
            for role in l_roles:
                if role[1] == Allow:
                    if not role[0] in roles:
                        roles.append(role[0])
                elif role[1] == Deny:
                    if role[0] in roles:
                        roles.remove(role[0])
        return roles
    
    principal = get_principal()
    log.debug("get_roles: principal id %s" % principal.id)
    pg = principal.groups.keys()
    # ensure that the actual principal.id is included
    if not principal.id in pg:
        pg.append(principal.id)
    log.debug("get_roles: principal groups %s" % pg)
    roles = []
    for principal_id in pg:
        roles = add_roles(principal_id, prms, roles)
    log.debug("get_roles: principal roles %s" % roles)
    return roles


def get_current_parliament_governments(parliament=None):
    if parliament is None: 
        parliament = get_current_parliament()
    import sqlalchemy.sql.expression as sql
    session = Session()
    governments = session.query(domain.Government).filter(
            sql.and_(domain.Government.parent_group_id==parliament.group_id,
                     domain.Government.status=='active')).all()
    return governments
    
def get_all_group_ids_in_parliament(parliament_id):
    """ get all groups (group_ids) in a parliament
    including the sub (e.g. ministries) groups """
    session = Session()
    group_ids = [parliament_id,]
    query = session.query(domain.Group).filter(
        domain.Group.parent_group_id == parliament_id).options(
            eagerload('contained_groups'), 
            )
    results = query.all()
    for result in results:
        group_ids.append(result.group_id)
        for group in result.contained_groups:
            group_ids.append(group.group_id)
    return group_ids
    
    
def get_ministries_for_user_in_government(user_id, government_id):
    """Get the ministries where user_id is a active member."""
    session = Session()
    query = session.query(domain.Ministry).join(domain.Minister).filter(
        rdb.and_(
            schema.user_group_memberships.c.user_id==user_id,
            schema.groups.c.parent_group_id==government_id,
            schema.groups.c.status=='active',
            schema.user_group_memberships.c.active_p==True))
    return query.all()
def get_ministry_ids_for_user_in_government(user_id, government_id):
    """Get the ministry ids where user_id is a active member."""
    return [ ministry.group_id for ministry in 
             get_ministries_for_user_in_government(user_id, government_id) ]
    '''
    # alternative approach to get ministry_ids: 
    connection = session.connection(domain.Group)
    ministries_ids_query = rdb.select([schema.groups.c.group_id],
        from_obj=[
        rdb.join(schema.groups, schema.user_group_memberships,
        schema.groups.c.group_id == schema.user_group_memberships.c.group_id),
        ],
        whereclause =
            rdb.and_(
            schema.user_group_memberships.c.user_id==user_id,
            schema.groups.c.parent_group_id==government_id,
            schema.groups.c.status=='active',
            schema.user_group_memberships.c.active_p==True))
    session = Session()
    connection = session.connection(domain.Group)
    return [ group_id[0] for group_id in 
             connection.execute(ministries_ids_query) ]
    '''


def get_offices_held_for_user_in_parliament(user_id, parliament_id):
    """ get the Offices (functions/titles) held by a user in a parliament """
    session = Session()
    connection = session.connection(domain.Group)
    group_ids = get_all_group_ids_in_parliament(parliament_id)
    offices_held = rdb.select([schema.groups.c.short_name,
        schema.groups.c.full_name,
        schema.groups.c.type,
        schema.user_role_types.c.user_role_name,
        schema.role_titles.c.start_date,
        schema.role_titles.c.end_date,
        schema.user_group_memberships.c.start_date,
        schema.user_group_memberships.c.end_date,
        ], 
        from_obj=[   
        rdb.join(schema.groups, schema.user_group_memberships,
        schema.groups.c.group_id == schema.user_group_memberships.c.group_id
            ).outerjoin(
            schema.role_titles, schema.user_group_memberships.c.membership_id==
            schema.role_titles.c.membership_id).outerjoin(
                schema.user_role_types,
                schema.role_titles.c.title_name_id ==
                schema.user_role_types.c.user_role_type_id)],
            whereclause =
            rdb.and_(
                schema.groups.c.group_id.in_(group_ids),
                schema.user_group_memberships.c.user_id == user_id),  
            order_by = [schema.user_group_memberships.c.start_date,
                        schema.user_group_memberships.c.end_date,
                        schema.role_titles.c.start_date, 
                        schema.role_titles.c.end_date]                                     
            )
    o_held = connection.execute(offices_held)
    return o_held            
    
def get_group_ids_for_user_in_parliament(user_id, parliament_id):
    """ get the groups a user is member of for a specific parliament """
    session = Session()
    connection = session.connection(domain.Group)
    group_ids  = get_all_group_ids_in_parliament(parliament_id)
    my_groups = rdb.select([schema.user_group_memberships.c.group_id],
        rdb.and_(schema.user_group_memberships.c.active_p == True,
            schema.user_group_memberships.c.user_id == user_id,
            schema.user_group_memberships.c.group_id.in_(group_ids)),
        distinct=True)
    my_group_ids = []
    for group_id in connection.execute(my_groups):
        my_group_ids.append(group_id[0])
    return my_group_ids
                                    
def get_parliament_for_group_id(group_id):
    if group_id is None:
        return None
    session = Session()
    group = session.query(domain.Group).get(group_id)
    if group.type == 'parliament':
        return group
    else:
        return get_parliament_for_group_id(group.parent_group_id)               
        
        
        
