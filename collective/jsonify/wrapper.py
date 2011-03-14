


class Wrapper(dict):
    """ Gets the data in a format that can be used by the
        transmogrifier blueprints in collective.jsonmigrator
    """

    def __init__(self, context):

        from Acquisition import aq_base
        from Products.CMFCore.utils import getToolByName

        self.context = aq_base(context)
        self._context = context
        self.portal = getToolByName(self._context, 'portal_url').getPortalObject()
        self.portal_utils = getToolByName(self._context, 'plone_utils')
        self.charset = self.portal.portal_properties.site_properties.default_charset
        if not self.charset: # newer seen it missing ... but users can change it
            self.charset = 'utf-8'

        for method in dir(self):
            if method.startswith('get_'):
                getattr(self, method)()

    def decode(self, s, encodings=('utf8', 'latin1', 'ascii')):
        """ Sometimes we have to guess charset
        """
        if self.charset:
            test_encodings = (self.charset, ) + encodings
        for encoding in test_encodings:
            try:
                return s.decode(encoding)
            except UnicodeDecodeError:
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
            :keys: _type
        """
        try:
            self['_type'] = self.context.portal_type
        except AttributeError:
            self['_type'] = ''

    def get_classname(self):
        """ Classname of object.

            :keys: _classname

            Sometimes in old Plone sites we dont know exactly which type we are using
        """
        self['_classname'] = self.context.__class__.__name__

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
            :keys: _permission_mapping
        """
        self['_permission_mapping'] = {}
        if getattr(self._context, 'permission_settings', False):
            roles = self._context.validRoles()
            ps = self._context.permission_settings()
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

    def get_owner(self):
        """ Object owner
            :keys: _owner
        """

        try:
            try:
                try:
                    self['_owner'] = self._context.getWrappedOwner().getId()
                except:
                    self['_owner'] = self._context.getOwner(info = 1).getId()
            except:
                self['_owner'] = self.context.getOwner(info = 1)[1]
        except:
            self['_owner'] = ''



    def get_workflowhistory(self):
        """ Workflow history
            :keys: _workflow_history

            Example:::

                lalala
        """
        self['_workflow_history'] = {}
        if getattr(self.context, 'workflow_history', False):
            import ipdb; ipdb.set_trace()
            # TODO: we need to see what default value should be
            workflow_history = self.context.workflow_history.data
            for w in workflow_history:
                for i, w2 in enumerate(workflow_history[w]):
                    workflow_history[w][i]['time'] = str(workflow_history[w][i]['time'])
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
        fields = self._context.schema.fields()
        for field in fields:
            fieldname = unicode(field.__name__)
            type_ = field.__class__.__name__

            if type_ in ['StringField', 'BooleanField', 'LinesField',
                    'IntegerField', 'TextField', 'SimpleDataGridField',
                    'FloatField', 'FixedPointField', 'TALESString',
                    'TALESLines', 'ZPTField']:

                try:
                    value = field.getRaw(self._context)
                except AttributeError:
                    value = field.get(self._context)

                if callable(value) is True:
                    value = value()

                if value and type_ in ['StringField', 'TextField']:
                    try:
                        value = value.decode(self.charset)
                    except AttributeError:
                        # maybe an int?
                        value = unicode(value)
                    except Exception, e:
                        raise Exception('problems with %s: %s' %
                                (self.context.absolute_url(), str(e)))

                if value:
                    try:
                        ct = field.getContentType(self.context)
                    except AttributeError:
                        ct = ''
                    self[unicode(fieldname)] = value
                    self[unicode('_content_type_')+fieldname] = ct

            elif type_ in ['DateTimeField']:
                value = str(field.get(self._context))
                if value:
                    self[unicode(fieldname)] = value

            elif type_ in ['ImageField', 'FileField']:
                fieldname = unicode('_datafield_'+fieldname)
                value = field.get(self._context)
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
                        fname = fname.decode(self.charset, 'ignore')
                    except AttributeError:
                        # maybe an int?
                        fname = unicode(fname)
                    except Exception, e:
                        raise Exception('problems with %s: %s' %
                                (self.context.absolute_url(), str(e)))

                    ctype = field.getContentType(self._context)
                    self[fieldname] = {
                        'data': value,
                        'size': size,
                        'filename': fname or '',
                        'content_type': ctype}

            elif type_ in ['ReferenceField']:
                value = field.get(self._context)
                if value:
                    import pdb; pdb.set_trace()

                # AT references
                #from Products.Archetypes.interfaces import IReferenceable
                #if IReferenceable.providedBy(obj):
                #    self['_atrefs'] = {}
                #    self['_atbrefs'] = {}
                #    relationships = obj.getRelationships()
                #    for rel in relationships:
                #        self['_atrefs'][rel] = []
                #        refs = obj.getRefs(relationship=rel)
                #        for ref in refs:
                #            self['_atrefs'][rel].append('/'.join(ref.getPhysicalPath()))
                #    brelationships = obj.getBRelationships()
                #    for brel in brelationships:
                #        self['_atbrefs'][brel] = []
                #        brefs = obj.getBRefs(relationship=brel)
                #        for bref in brefs:
                #            self['_atbrefs'][brel].append('/'.join(bref.getPhysicalPath()))

            elif type_ in ['ComputedField']:
                continue

            else:
                raise TypeError('Unknown field type for ArchetypesWrapper in '
                        '%s in %s' % (fieldname, self.context.absolute_url()))

