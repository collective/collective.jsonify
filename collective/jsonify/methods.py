
import sys
import pprint
import traceback
import simplejson
from collective.jsonify.wrapper import Wrapper, WrapperWithoutFile
from AccessControl.SecurityManagement import newSecurityManager

def get_item(self):
    """
    """
    try:
        context_dict = WrapperWithoutFile(self)
    except Exception, e:
        tb = pprint.pformat(traceback.format_tb(sys.exc_info()[2]))
        return 'ERROR: exception wrapping object: %s\n%s' % (str(e), tb)

    for key in context_dict.keys():
        if key.startswith('_datafield_'):
            context_dict.pop(key)
    
    try:
        JSON = simplejson.dumps(context_dict)
    except Exception, e:
        return 'ERROR: wrapped object is not serializable: %s' % str(e)

    return JSON

def get_item_with_file(self):
    try:
        #use newSecurityManager
        newSecurityManager(
           self.portal_url.getPortalObject(),
           self.portal_url.getPortalObject().getOwner()
           )
        context_dict = Wrapper(self)
    except Exception, e:
        tb = pprint.pformat(traceback.format_tb(sys.exc_info()[2]))
        return 'ERROR: exception wrapping object: %s\n%s' % (str(e), tb)

    try:
        JSON = simplejson.dumps(context_dict)

    except Exception, e:
        return 'ERROR: wrapped object is not serializable: %s' % str(e)

    return JSON


def get_children(self):
    """
    """
    from Acquisition import aq_base

    children = []
    if getattr(aq_base(self), 'objectIds', False):
        children = self.objectIds()
        # Btree based folders return an OOBTreeItems object which is not serializable
        # Thus we need to convert it to a list
        if not isinstance(children, list):
            children = [item for item in children]
    return simplejson.dumps(children)
