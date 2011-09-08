import base64
import sys
import pprint
import traceback
import simplejson

from collective.jsonify.wrapper import Wrapper


def get_item(self):
    """
    """

    try:
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

def get_catalog_results(self):
    """Returns a list of paths of all items found by the catalog.
       Query parameters can be passed in the request.
    """
    if not hasattr(self.aq_base, 'unrestrictedSearchResults'):
        return
    query = self.REQUEST.form.get('catalog_query', None)
    if query:
        query = eval(base64.b64decode(query),
                     {"__builtins__": None}, {})
    item_paths = [item.getPath() for item 
                  in self.unrestrictedSearchResults(**query) ]
    return simplejson.dumps(item_paths)
