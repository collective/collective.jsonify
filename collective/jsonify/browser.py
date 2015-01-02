from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from collective.jsonify.wrapper import Wrapper

try:
    from hashlib import md5
except ImportError:
    from md5 import md5

try:
    import simplejson as json
except:
    import json


class JsonifyView(BrowserView):
    """Parameters:

    ACTIONS: QUERY -> use portal_catalog for data retrieving
             LIST -> use portal_catalog but return COMPACT list of live objects
             GET -> return the actual JSON of the objects (really needed?)
             PUT -> add object
             PATCH -> update object (just modified fields will be passed)
             DELETE -> delete object from portal
    """

    def __call__(self):
        self.params = self.request.form
        self.send_bin = self.params.get('send_bin', False)
        self.absolute_urls = self.params.get('absolute_urls', True)
        self.available = 'available' in self.params
        if not('action' in self.params):
            return
        if (self.params['action'] == 'query'):
            objs = self.action_query()
            # Do not return any object, just check for it
            if self.available:
                if (objs):
                    return len(objs)
                else:
                    return
            else:
                return self.get_it_out(objs)
        if (self.params['action'] == 'list'):
            raw_objs = self.action_query()
            return self.action_list(raw_objs)

    def action_list(self, raw_objs):
        objs = [
            {"uid": raw_obj.UID(),
             "path": "/".join(raw_obj.getPhysicalPath())}
            for raw_obj in raw_objs
        ]
        return self.push_json(objs)

    def action_query(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        if self.params:
            query = self.params
            query.pop('action', None)
            query.pop('send_bin', None)
            query.pop('absolute_urls', None)
            query.pop('available', None)
            query['path'] = '/'.join(self.context.getPhysicalPath())

        brains = catalog.searchResults(query)
        return [brain.getObject() for brain in brains if brain]

    def url_replacer(self, obj, searchstring, lookfor):
        """ this is to replace JUST relative urls with absolute urls
        """
        context = aq_inner(self.context)
        root = getToolByName(context, 'portal_url').getPortalObject()
        position = 0
        for found in range(searchstring.count(lookfor)):
            position = searchstring.index(lookfor, position)
            poslookfor = position + len(lookfor)
            if searchstring[poslookfor:poslookfor + 4] != 'http':
                if searchstring[poslookfor:poslookfor + 1] == '/':
                    # it's a relative url to the root - use root.absolute_url()
                    url_to_add = root.absolute_url()
                else:
                    # it's a relative url to the actual object position
                    url_to_add = obj.aq_parent.aq_inner.absolute_url() + '/'
                searchstring = searchstring[:position] +\
                    lookfor + url_to_add + searchstring[poslookfor:]
                position = poslookfor + 4
            else:
                position = poslookfor
        return searchstring

    def get_it_out(self, raws):
        objs = []
        for raw in raws:
            wrapped = Wrapper(raw)
            for key in wrapped.keys():
                if key.startswith('_datafield_'):
                    # get HASH: useful to check changes with APP side before
                    # download it
                    m = md5()
                    m.update(wrapped[key]['data'])
                    wrapped[key]['md5'] = m.hexdigest()
                    if not(self.send_bin):
                        wrapped[key]['data'] = ''
                else:
                    if self.absolute_urls and self.absolute_urls != 'False':
                        if type(wrapped[key]) in (unicode, str):
                            for tosearch in ['src=\"', 'href=\"']:
                                wrapped[key] = self.url_replacer(
                                    raw,
                                    wrapped[key],
                                    tosearch
                                )

            objs.append(wrapped)
        return self.push_json(objs)

    def push_json(self, objs):
        try:
            JSON = json.dumps(objs)
            self.request.response.setHeader("Content-type", "application/json")
            return JSON
        except Exception, e:
            return 'ERROR: wrapped object is not serializable: %s' % str(e)
