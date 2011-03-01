
from Acquisition import aq_base
from zope.annotation.interfaces import IAnnotations
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.CatalogTool import getObjPositionInParent


class ZopeBaseWrapper(dict):
    """PropertyManager properties, format and default view,
       access control, workflow history,
       and pass it as tranmogrifier friendly style

       Gets the data in a format that can be used by the
       transmogrifier blueprints in collective.blueprint.jsonmigrator
    """

    def __init__(self, obj):
        self.obj = aq_base(obj)

        self.portal = getToolByName(obj, 'portal_url').getPortalObject()
        self.portal_utils = getToolByName(obj, 'plone_utils')
        self.charset = self.portal.portal_properties.site_properties.default_charset

        if not self.charset: # newer seen it missing ... but users can change it
            self.charset = 'utf-8'

        self['_path'] = '/'.join(obj.getPhysicalPath())

        self['_type'] = self.obj.__class__.__name__
        try:
            self['_portal_type'] = self.obj.portal_type
        except AttributeError:
            self['_portal_type'] = ''

        # properties
        self['_properties'] = []
        if getattr(self.obj, 'propertyIds', False):
            for pid in self.obj.propertyIds():
                val = self.obj.getProperty(pid)
                typ = self.obj.getPropertyType(pid)
                if typ == 'string':
                    if getattr(val, 'decode', False):
                        try:
                            val = val.decode(self.charset, 'ignore')
                        except UnicodeEncodeError:
                            val = unicode(val)
                    else:
                        val = unicode(val)
                self['_properties'].append((pid, val,
                                       self.obj.getPropertyType(pid)))

        # default view
        try:
            _browser = '/'.join(self.portal_utils.browserDefault(self.obj)[1])
            if _browser not in ['folder_listing', 'index_html']:
                self['_layout'] = ''
                self['_defaultpage'] = _browser
        except AttributeError:
            _browser = obj.getLayout()
            self['_layout'] = _browser
            self['_defaultpage'] = ''

        # format
        self['_content_type'] = obj.Format()

        # local roles
        self['_ac_local_roles'] = {}
        if getattr(self.obj, '__ac_local_roles__', False):
            for key, val in obj.__ac_local_roles__.items():
                if key is not None:
                    self['_ac_local_roles'][key] = val

        self['_userdefined_roles'] = ()
        if getattr(self.obj, 'userdefined_roles', False):
            self['_userdefined_roles'] = obj.userdefined_roles()

        self['_permission_mapping'] = {}
        if getattr(self.obj, 'permission_settings', False):
            roles = obj.validRoles()
            ps = obj.permission_settings()
            for perm in ps:
                unchecked = 0
                if not perm['acquire']:
                    unchecked = 1
                new_roles = []
                for role in perm['roles']:
                    if role['checked']:
                        role_idx = role['name'].index('r')+1
                        role_name = roles[int(role['name'][role_idx:])]
                        new_roles.append(role_name)
                if unchecked or new_roles:
                    self['_permission_mapping'][perm['name']] = \
                         {'acquire': not unchecked,
                          'roles': new_roles}

        if getattr(self.obj, 'getWrappedOwner', False):
            self['_owner'] = (1, obj.getWrappedOwner().getId())
        else:
            # fallback
            # not very nice but at least it works
            # trying to get/set the owner via getOwner(), changeOwnership(...)
            # did not work, at least not with plone 1.x, at 1.0.1, zope 2.6.2
            self['_owner'] = (0, obj.getOwner(info = 1).getId())

        # workflow history
        if getattr(self.obj, 'workflow_history', False):
            workflow_history = obj.workflow_history.data
            for w in workflow_history:
                for i, w2 in enumerate(workflow_history[w]):
                    workflow_history[w][i]['time'] = str(workflow_history[w][i]['time'])
                    workflow_history[w][i]['comments'] = workflow_history[w][i]['comments'].decode(self.charset, 'ignore')
            self['_workflow_history'] = workflow_history

        # obj position in parent
        self['_gopip'] = getObjPositionInParent(obj)

        # annotations
        try:
            annotations = IAnnotations(obj)
        except TypeError:
            pass
        else:
            for key in annotations:
                if not key.startswith('Archetypes.storage.AnnotationStorage'):
                    pass

    def decode(self, s, encodings=('utf8', 'latin1', 'ascii')):
        if self.charset:
            test_encodings = (self.charset, ) + encodings
        for encoding in test_encodings:
            try:
                return s.decode(encoding)
            except UnicodeDecodeError:
                pass
        return s.decode(test_encodings[0], 'ignore')


class BaseWrapper(ZopeBaseWrapper):
    """Wraps (CMF) dublin core metadata
    """

    def __init__(self, obj):
        super(BaseWrapper, self).__init__(obj)

        # Dublin Core
        self['id'] = self.obj.getId()
        for field in ('title', 'description', 'rights', 'language'):
            val = getattr(self.obj, field, False)
            if val:
                self[field] = val.decode(self.charset, 'ignore')
        # for DC attrs that are tuples
        for attr in ('subject', 'contributors'):
            self[attr] = []
            val_tuple = getattr(self.obj, attr, False)
            if val_tuple:
                for val in val_tuple:
                    self[attr].append(val.decode(self.charset, 'ignore'))
                self[attr] = tuple(self[attr])
        # for DC attrs that are DateTimes
        datetimes_dict = {'creation_date': 'creation_date',
                          'modification_date': 'modification_date',
                          'expiration_date': 'expirationDate',
                          'effective_date': 'effectiveDate',
                          'expirationDate': 'expirationDate',
                          'effectiveDate': 'effectiveDate'}
        for old_name, new_name in datetimes_dict.items():
            val = getattr(self.obj, old_name, False)
            if val:
                self[new_name] = str(val)


class ZopeObjectWrapper(ZopeBaseWrapper):

    def __init__(self, obj):
        super(ZopeObjectWrapper, self).__init__(obj)
        self['document_src'] = self.decode(self.obj.document_src())
