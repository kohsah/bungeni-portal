# -*- coding: utf-8 -*-
#
# File: Ministry.py
#
# Copyright (c) 2007 by []
# Generator: ArchGenXML Version 1.6.0-beta-svn
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

__author__ = """Jean Jordaan <jean.jordaan@gmail.com>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from zope import interface
from Products.Relations.field import RelationField
from Products.Bungeni.config import *

##code-section module-header #fill in your manual code here
##/code-section module-header

schema = Schema((

    StringField(
        name='shortTitle',
        widget=StringWidget(
            label='Shorttitle',
            label_msgid='Bungeni_label_shortTitle',
            i18n_domain='Bungeni',
        )
    ),

    RelationField(
        name='ministrys',
        widget=ReferenceWidget(
            label='Ministrys',
            label_msgid='Bungeni_label_ministrys',
            i18n_domain='Bungeni',
        ),
        multiValued=1,
        relationship='supersedes'
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

Ministry_schema = BaseFolderSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class Ministry(BaseFolder):
    """
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(BaseFolder,'__implements__',()),)

    # This name appears in the 'add' box
    archetype_name = 'Ministry'

    meta_type = 'Ministry'
    portal_type = 'Ministry'
    allowed_content_types = ['Portfolio']
    filter_content_types = 1
    global_allow = 0
    #content_icon = 'Ministry.gif'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "Ministry"
    typeDescMsgId = 'description_edit_ministry'

    _at_rename_after_creation = True

    schema = Ministry_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods


registerType(Ministry, PROJECTNAME)
# end of class Ministry

##code-section module-footer #fill in your manual code here
##/code-section module-footer



