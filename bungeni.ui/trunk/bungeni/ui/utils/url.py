# Bungeni Parliamentary Information System - http://www.bungeni.org/
# Copyright (C) 2010 - Africa i-Parliaments - http://www.parliaments.info/
# Licensed under GNU GPL v2 - http://www.gnu.org/licenses/gpl-2.0.txt
'''URL path/name utilities for the UI

recommended usage:
from bungeni.ui.utils import url

$Id$
'''

def urljoin(base, action):
    if action is None:
        return
    if action.startswith('http://') or action.startswith('https://'):
        return action
    if action.startswith('/'):
        raise NotImplementedError(action)

    return "/".join((base, action.lstrip('./')))

# XXX tmp hack -- business/whats-on -- because the "index" of the business 
# section is actually called "whats-on", we also check and remove that
# TODO rename business/whats-on to business/index
indexNames = ("index", "index.html", "@@index.html", "whats-on")

def absoluteURL(context, request):
    """
    For cleaner public URLs, we ensure to use an empty string instead of 'index'.
    
    Throughout bungeni and ploned packages, this function should ALWAYS be
    used instead of zope.traversing.browser.absoluteURL.
    """
    import logging; log = logging.getLogger('bungeni.ui.utils');
    from zope.traversing import browser
    url = browser.absoluteURL(context, request).split("/")
    while url[-1] in indexNames:
        log.warning(" POPPING: %s -> %s" % ('/'.join(url), url[-1]))
        url.pop()
    return '/'.join(url)

def same_path_names(base_path_name, path_name):
    """ (base_path_name, path_name) -> bool
    
    Checks if the two url path names are "equivalent" -- considering the case 
    for "" as base_path_name implying that we should be at an "index" URL node.
    """
    if base_path_name!=path_name:
        if base_path_name=="": # empty string -> index
            if path_name in indexNames:
                return True
    return base_path_name==path_name

