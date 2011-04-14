


class Wrapper(dict):
    """ Gets the data in a format that can be used by the
        transmogrifier blueprints in collective.jsonmigrator
    """

    def __init__(self, context):

        from Acquisition import aq_base
        from Products.CMFCore.utils import getToolByName

        self.context = context
        self._context = aq_base(context)
        self.portal = getToolByName(self.context, 'portal_url').getPortalObject()
        self.portal_path = '/'.join(self.portal.getPhysicalPath())
        self.portal_utils = getToolByName(self.context, 'plone_utils')
        self.charset = self.portal.portal_properties.site_properties.default_charset
        if not self.charset: # newer seen it missing ... but users can change it
            self.charset = 'utf-8'

        for method in dir(self):
            if method.startswith('get_'):
                getattr(self, method)()

    def decode(self, s, encodings=('utf8', 'latin1', 'ascii')):
        """ Sometimes we have to guess charset
        """
        if type(s) is unicode:
            return s
        if self.charset:
            test_encodings = (self.charset, ) + encodings
        for encoding in test_encodings:
            try:
                return s.decode(encoding)
            except:
                pass
        return s.decode(test_encodings[0], 'ignore')


    def get_path(self):
        """ Path of object

            Example::

                {'_path': '/Plone/first-page'}

        """
        self['_path'] = '/'.join(self.context.getPhysicalPath())

    def get_type(self):
        """ Portal type of object

            Example::
                {'_type': 'Document'}
        """
        try:
            self['_type'] = self.context.portal_type
        except AttributeError:
            pass

    def get_classname(self):
        """ Classname of object.

            Sometimes in old Plone sites we dont know exactly which type we are
            using.

            Example::

                {'_classname': 'ATDocument'}

        """
        self['_classname'] = self.context.__class__.__name__

    def get_uid(self):
        """ Unique ID of object

            Example::

                {'_uid': '12jk3h1kj23h123jkh13kj1k23jh1'}
        """
        if hasattr(self._context, 'UID'):
            self['_uid'] = self.context.UID()

    def get_properties(self):
        """ Object properties
            :keys: _properties
        """
        self['_properties'] = []
        if getattr(self.context, 'propertyIds', False):
            for pid in self.context.propertyIds():
                val = self.context.getProperty(pid)
                typ = self.context.getPropertyType(pid)
                if typ == 'string':
                    val = self.decode(val)
                self['_properties'].append(
                        (pid, val, self.context.getPropertyType(pid)))

    def get_defaultview(self):
        """ Default view of object
            :keys: _layout, _defaultpage
        """
        try:
            _browser = '/'.join(self.portal_utils.browserDefault(self.context)[1])
            if _browser not in ['folder_listing', 'index_html']:
                self['_layout'] = ''
                self['_defaultpage'] = _browser
        except AttributeError:
            _browser = self.context.getLayout()
            self['_layout'] = _browser
            self['_defaultpage'] = ''

    def get_format(self):
        """ Format of object
            :keys: _format
        """
        self['_content_type'] = self.context.Format()

    def get_local_roles(self):
        """ Local roles of object
            :keys: _local_roles
        """
        self['_local_roles'] = {}
        if getattr(self.context, '__local_roles__', False):
            for key, val in self.context.__ac_local_roles__.items():
                if key is not None:
                    self['_local_roles'][key] = val

    def get_userdefined_roles(self):
        """ User defined roles for object (via sharing UI)
            :keys: _userdefined_roles
        """
        self['_userdefined_roles'] = ()
        if getattr(self.context, 'userdefined_roles', False):
            self['_userdefined_roles'] = self.context.userdefined_roles()

    def get_permissions(self):
        """ Permission of object (Security tab in ZMI)
            :keys: _permissions
        """
        self['_permissions'] = {}
        if getattr(self.context, 'permission_settings', False):
            roles = self.context.validRoles()
            ps = self.context.permission_settings()
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
                    self['_permissions'][perm['name']] = \
                         {'acquire': not unchecked,
                          'roles': new_roles}

    def get_owner(self):
        """ Object owner
            :keys: _owner
        """

        try:
            try:
                try:
                    self['_owner'] = self.context.getWrappedOwner().getId()
                except:
                    self['_owner'] = self.context.getOwner(info = 1).getId()
            except:
                self['_owner'] = self.context.getOwner(info = 1)[1]
        except:
            pass

    def get_workflowhistory(self):
        """ Workflow history
            :keys: _workflow_history

            Example:::

                lalala
        """
        self['_workflow_history'] = {}
        if getattr(self.context, 'workflow_history', False):
            workflow_history = self.context.workflow_history.data
            for w in workflow_history:
                for i, w2 in enumerate(workflow_history[w]):
                    if 'time' in workflow_history[w][i].keys():
                        workflow_history[w][i]['time'] = str(workflow_history[w][i]['time'])
                    if 'comments' in workflow_history[w][i].keys():
                        workflow_history[w][i]['comments'] = self.decode(workflow_history[w][i]['comments'])
            self['_workflow_history'] = workflow_history

    def get_position_in_parent(self):
        """ Get position in parent
            :keys: _gopip
        """
        from Products.CMFPlone.CatalogTool import getObjPositionInParent
        self['_gopip'] = getObjPositionInParent(self.context)

    def get_id(self):
        """ Object id
            :keys: _id
        """
        self['_id'] = self.context.getId()

    # TODO: this should be only for non archetypes
    #def get_dublin_core(self):
    #    # string
    #    for field in ('title', 'description', 'rights', 'language'):
    #        val = getattr(self.context, field, False)
    #        if val:
    #            self[field] = self.decode(val)
    #        else:
    #            self[field] = ''
    #    # tuple
    #    for field in ('subject', 'contributors'):
    #        self[field] = []
    #        val_tuple = getattr(self.context, field, False)
    #        if val_tuple:
    #            for val in val_tuple:
    #                self[field].append(self.decode(val))
    #            self[field] = tuple(self[field])
    #        else:
    #            self[field] = ()
    #    # datetime
    #    #TODO
    #    for field in ['creation_date', 'modification_date', 'expiration_date',
    #                  'effective_date', 'expirationDate', 'effectiveDate']:
    #        val = getattr(self.context, field, False)
    #        if val:
    #            self[field] = str(val)
    #        else:
    #            self[field] = ''

    def get_zopeobject_document_src(self):
        document_src = getattr(self.context, 'document_src', None)
        if document_src:
            self['document_src'] = self.decode(document_src())
        else:
            self['_zopeobject_document_src'] = ''

    def get_archetypes_fields(self):
        """ If Archetypes is used then dump schema
        """

        try:
            from Products.Archetypes.interfaces import IBaseObject
            if not IBaseObject.providedBy(self.context):
                return
        except:
            return

        import base64
        fields = self.context.schema.fields()
        for field in fields:
            fieldname = unicode(field.__name__)
            type_ = field.__class__.__name__

            if type_ in ['StringField', 'BooleanField', 'LinesField',
                    'IntegerField', 'TextField', 'SimpleDataGridField',
                    'FloatField', 'FixedPointField', 'TALESString',
                    'TALESLines', 'ZPTField', 'DataGridField', 'EmailField']:

                try:
                    value = field.getRaw(self.context)
                except AttributeError:
                    value = field.get(self.context)

                if callable(value) is True:
                    value = value()

                if value and type_ in ['StringField', 'TextField']:
                    try:
                        value = self.decode(value)
                    except AttributeError:
                        # maybe an int?
                        value = unicode(value)
                    except Exception, e:
                        raise Exception('problems with %s: %s' %
                                (self.context.absolute_url(), str(e)))
                elif value and type_ == 'DataGridField':
                     for i, row in enumerate(value):
                         for col_key in row.keys():
                             col_value = row[col_key]
                             if type(col_value) in (unicode, str):
                                 value[i][col_key] = self.decode(col_value)

                if value:
                    try:
                        ct = field.getContentType(self.context)
                    except AttributeError:
                        ct = ''
                    self[unicode(fieldname)] = value
                    self[unicode('_content_type_')+fieldname] = ct

            elif type_ in ['DateTimeField']:
                value = str(field.get(self.context))
                if value:
                    self[unicode(fieldname)] = value

            elif type_ in ['ImageField', 'FileField', 'AttachmentField']:
                fieldname = unicode('_datafield_'+fieldname)
                value = field.get(self.context)
                value2 = value

                if type(value) is not str:
                    if type(value.data) is str:
                        value = base64.b64encode(value.data)
                    else:
                        data = value.data
                        value = ''
                        while data is not None:
                            value += data.data
                            data = data.next
                        value = base64.b64encode(value)

                # limit size of attachments to 20M
                # TODO: this should be configurable
                if value and len(value) < 20000000:
                    size = value2.getSize()
                    fname = field.getFilename(self.context)
                    try:
                        fname = self.decode(fname)
                    except AttributeError:
                        # maybe an int?
                        fname = unicode(fname)
                    except Exception, e:
                        raise Exception('problems with %s: %s' %
                                (self.context.absolute_url(), str(e)))

                    ctype = field.getContentType(self.context)
                    self[fieldname] = {
                        'data': value,
                        'size': size,
                        'filename': fname or '',
                        'content_type': ctype}

            elif type_ in ['ReferenceField']:
                pass

            elif type_ in ['ComputedField']:
                continue

            else:
                raise TypeError('Unknown field type for ArchetypesWrapper in '
                        '%s in %s' % (fieldname, self.context.absolute_url()))

    def get_references(self):
        """ AT references
        """
        try:
            from Products.Archetypes.interfaces import IReferenceable
            if not IReferenceable.providedBy(self.context):
                return
        except:
            return

        self['_atrefs'] = {}
        self['_atbrefs'] = {}
        relationships = self.context.getRelationships()
        for rel in relationships:
            self['_atrefs'][rel] = []
            refs = self.context.getRefs(relationship=rel)
            for ref in refs:
                if ref is not None:
                    self['_atrefs'][rel].append('/'.join(ref.getPhysicalPath()))
        brelationships = self.context.getBRelationships()
        for brel in brelationships:
            self['_atbrefs'][brel] = []
            brefs = self.context.getBRefs(relationship=brel)
            for bref in brefs:
                if bref is not None:
                    self['_atbrefs'][brel].append('/'.join(bref.getPhysicalPath()))

    def get_translation(self):
        """ Get LinguaPlone translation linking information.
        """
        if not hasattr(self._context, 'getCanonical'):
            return
        self['_translationOf'] = '/'.join(self.context.getCanonical(
                                 ).getPhysicalPath())[len(self.portal_path):]
        self['_canonicalTranslation'] = self.context.isCanonical()
