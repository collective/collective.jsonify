###############################################################################
#####                                                                     #####
#####   IMPORTANT, READ THIS !!!                                          #####
#####   ------------------------                                          #####
#####                                                                     #####
#####   Bellow are 2 external methods which you enable by adding them     #####
#####   into your Plone site. For that, you must link this file in your   #####
#####   Extensions directory, and replace the path_to_export_wrappers     #####
#####   with the path to your export_wrappers (s).                        #####
#####   You can also customize the _WRAPPERS dictionaries to suit         #####
#####   your nedds.                                                       #####
#####                                                                     #####
###############################################################################


import sys
import traceback
import pprint
from os import path
import simplejson
from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.interfaces import IBaseObject

# path_to_export_wrappers = path.dirname(path.abspath(__file__))

sys.path.append('/home/www/ucaout/collective.sync_migrator/collective/sync_migrator/browser/export_wrappers')


from base_wrapper import BaseWrapper, ZopeObjectWrapper
from atcontent_wrapper import ArchetypesWrapper


# PT_WRAPPERS is a dictionary from portal_types to wrapper classes.
# CLASS_WRAPPERS is a dictionary from class names to wrapper classes.
# wrapper classes extend from export_wrappers.cmf_wrappers.BaseWrapper
# or any of its derived classes.
PT_WRAPPERS = {

}

CLASS_WRAPPERS = {
    'DTMLMethod':               ZopeObjectWrapper,
    'ZopePageTemplate':         ZopeObjectWrapper,
    'PythonScript':             ZopeObjectWrapper,
}


def export_json_item(self, path=''):
    """
    use as a external method named export_json_item
    """
    portal = getToolByName(self, 'portal_url').getPortalObject()
    #self.request.RESPONSE.setHeader('content-type', 'text/plain')
    try:
        obj = portal.unrestrictedTraverse(path)
    except AttributeError:
        return 'ERROR: object not found'
    try:
        wrapper = PT_WRAPPERS[aq_base(obj).portal_type]
    except (KeyError, AttributeError):
        try:
            wrapper = CLASS_WRAPPERS[obj.__class__.__name__]
        except KeyError:
            if IBaseObject.providedBy(obj):
                wrapper = ArchetypesWrapper
            else:
                wrapper = BaseWrapper
    try:
        obj_dict = wrapper(obj)
    except Exception, e:
        tb = pprint.pformat(traceback.format_tb(sys.exc_info()[2]))
        return 'ERROR: exception wrapping object: %s\n%s' % (str(e), tb)
    try:
        obj_str = simplejson.dumps(obj_dict)
    except Exception, e:
        return 'ERROR: wrapped object is not serializable: %s' % str(e)
    return obj_str


def list_item_children(self, path=''):
    """
    use as a external method named list_item_children
    """
    portal = getToolByName(self, 'portal_url').getPortalObject()
    #self.request.RESPONSE.setHeader('content-type', 'text/plain')
    try:
        obj = portal.unrestrictedTraverse(path)
    except AttributeError:
        return 'ERROR: parent object not found'
    children = []
    if getattr(aq_base(obj), 'objectValues', False):
        children = obj.objectIds()
#        for child in obj.objectValues():
#            if getattr(aq_base(child), 'portal_type', '') in PT_WRAPPERS.keys():
#                children.append(child.getId())
#            elif child.__class__.__name__ in CLASS_WRAPPERS.keys():
#                children.append(child.getId())
    return simplejson.dumps(children)


def get_modification_date(self, path=''):
    """
    use as a external method named get_modification_date
    """
    portal = getToolByName(self, 'portal_url').getPortalObject()
    #self.request.RESPONSE.setHeader('content-type', 'text/plain')
    try:
        obj = portal.unrestrictedTraverse(path)
    except AttributeError:
        return 'ERROR: object not found'
    try:
        return str(obj.modified())
    except AttributeError:
        return '+'


def uid_to_path(self, uid):
    """
    Use as external method named uid_to_path
    """
    uc = getToolByName(self, 'uid_catalog')
    brains = uc(UID=uid)
    try:
        b = brains[0]
    except IndexError:
        return ''
    return '/'.join(b.getObject().getPhysicalPath())

