import base64
import sys
import pprint
import traceback
from collective.jsonify.wrapper import Wrapper, WrapperWithoutFile, DiscussionItemWrapper
from collective.jsonify.dashboard import DashboardWrapper
from AccessControl.SecurityManagement import newSecurityManager

try:
    import simplejson as json
except:
    import json



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
        JSON = json.dumps(context_dict)
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
        JSON = json.dumps(context_dict)
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
    return json.dumps(children)

def get_catalog_results(self):
    """Returns a list of paths of all items found by the catalog.
       Query parameters can be passed in the request.
    """
    if not hasattr(self.aq_base, 'unrestrictedSearchResults'):
        return
    query = self.REQUEST.form.get('catalog_query', None)
    from Products.ZCatalog.ZCatalog import ZCatalog
    if query:
        query = eval(base64.decodestring(query),
                     {"__builtins__": None}, {})
    item_paths = [item.getPath() for item in ZCatalog.searchResults(self, **query)]
    
    return json.dumps(item_paths)

def get_users(self):
    """return all userids used for export the dashboards"""

    userids = [user['userid'] for user in self.acl_users.searchUsers()]
    return json.dumps(userids)

def get_dashboards(self):
    """Return the dashboard from the given user
    """

    userid = self.REQUEST.get('userid', '')

    try:
        context_dict = DashboardWrapper(self, userid)
    except Exception, e:
        tb = pprint.pformat(traceback.format_tb(sys.exc_info()[2]))
        return 'ERROR: exception wrapping object: %s\n%s' % (str(e), tb)

    try:
        JSON = json.dumps(context_dict)
    except Exception, e:
        return 'ERROR: wrapped object is not serializable: %s' % str(e)

    return JSON


def get_discussion_item(self):
    """Return the disscusion item relevant attributes.
    """

    try:
        context_dict = DiscussionItemWrapper(self)
    except Exception, e:
        tb = pprint.pformat(traceback.format_tb(sys.exc_info()[2]))
        return 'ERROR: exception wrapping object: %s\n%s' % (str(e), tb)

    for key in context_dict.keys():
        if key.startswith('_datafield_'):
            context_dict.pop(key)

    try:
        JSON = json.dumps(context_dict)
    except Exception, e:
        return 'ERROR: wrapped object is not serializable: %s' % str(e)

    return JSON
