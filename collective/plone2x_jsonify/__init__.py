
import sys
import pprint
import traceback
import simplejson

from Acquisition import aq_base

try:
    from Products.Archetypes.interfaces import IBaseObject
except:
    IBaseObject = None

from collective.plone2x_jsonify import config
from collective.plone2x_jsonify.base import BaseWrapper
from collective.plone2x_jsonify.base import DCWrapper
from collective.plone2x_jsonify.base import ZopeBaseWrapper
from collective.plone2x_jsonify.at import ArchetypesWrapper
from collective.plone2x_jsonify.cmf import DocumentWrapper
from collective.plone2x_jsonify.cmf import LinkWrapper
from collective.plone2x_jsonify.cmf import NewsItemWrapper
from collective.plone2x_jsonify.cmf import ListCriteriaWrapper
from collective.plone2x_jsonify.cmf import StringCriteriaWrapper
from collective.plone2x_jsonify.cmf import DateCriteriaWrapper
from collective.plone2x_jsonify.cmf import FileWrapper
from collective.plone2x_jsonify.cmf import ImageWrapper
from collective.plone2x_jsonify.cmf import EventWrapper


def get_item(context):
    """
    json representation of single object
    """

    try:
        wrapper = config.PORTALTYPE_WRAPPERS[aq_base(context).portal_type]
    except (KeyError, AttributeError):
        try:
            wrapper = config.CLASSNAME_WRAPPERS[context.__class__.__name__]
        except KeyError:
            if IBaseObject and IBaseObject.providedBy(context):
                wrapper = ArchetypesWrapper
            else:
                wrapper = BaseWrapper

    try:
        obj_dict = wrapper(context)
    except Exception, e:
        tb = pprint.pformat(traceback.format_tb(sys.exc_info()[2]))
        return 'ERROR: exception wrapping object: %s\n%s' % (str(e), tb)

    try:
        JSON = simplejson.dumps(obj_dict)
    except Exception, e:
        return 'ERROR: wrapped object is not serializable: %s' % str(e)

    context.request.RESPONSE.setHeader('content-type', 'application/json')
    return JSON


def get_children(context):
    children = []
    if getattr(aq_base(context), 'objectIds', False):
        children = context.objectIds()
    return simplejson.dumps(children)


def get_modification_date(context):
    try:
        return str(obj.modified())
    except AttributeError:
        return '+'


#def uid_to_path(self, uid):
#    """
#    Use as external method named uid_to_path
#    """
#    uc = getToolByName(self, 'uid_catalog')
#    brains = uc(UID=uid)
#    try:
#        b = brains[0]
#    except IndexError:
#        return ''
#    return '/'.join(b.getObject().getPhysicalPath())
