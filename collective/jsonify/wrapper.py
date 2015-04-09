from Acquisition import aq_base
from DateTime import DateTime
import datetime
import os


class Wrapper(dict):
    """Gets the data in a format that can be used by the transmogrifier
    blueprints in collective.jsonmigrator.
    """

    def __init__(self, context):
        self.context = context
        self._context = aq_base(context)
        self.charset = None
        try:
            from Products.CMFCore.utils import getToolByName
            self.portal = getToolByName(
                self.context, 'portal_url').getPortalObject()
            self.portal_path = '/'.join(self.portal.getPhysicalPath())
            self.portal_utils = getToolByName(
                self.context, 'plone_utils', None)
            try:
                self.charset = self.portal.portal_properties.site_properties.default_charset  # noqa
            except AttributeError:
                pass
        except ImportError:
            pass

        # never seen it missing ... but users can change it
        if not self.charset:
            self.charset = 'utf-8'

        for method in dir(self):
            if method.startswith('get_'):
                getattr(self, method)()

    def providedBy(self, iface, ctx):
        # Handle zope.interface and Interface interfaces.
        if getattr(iface, 'providedBy', False):
            ret = iface.providedBy(ctx)
        elif getattr(iface, 'isImplementedBy', False):
            ret = iface.isImplementedBy(ctx)
        return bool(ret)

    def decode(self, s, encodings=('utf8', 'latin1', 'ascii')):
        """Sometimes we have to guess charset
        """
        if callable(s):
            s = s()
        if isinstance(s, unicode):
            return s
        test_encodings = encodings
        if self.charset:
            test_encodings = (self.charset, ) + test_encodings
        for encoding in test_encodings:
            try:
                return s.decode(encoding)
            except:
                pass
        return s.decode(test_encodings[0], 'ignore')

    def get_dexterity_fields(self):
        """If dexterity is used then extract fields.
        """
        try:
            from plone.dexterity.interfaces import IDexterityContent
            if not self.providedBy(IDexterityContent, self.context):
                return
            from plone.dexterity.utils import iterSchemata
            # from plone.uuid.interfaces import IUUID
            from zope.schema import getFieldsInOrder
            from datetime import date
        except:
            return

        # get all fields for this obj
        for schemata in iterSchemata(self.context):
            for fieldname, field in getFieldsInOrder(schemata):
                try:
                    value = field.get(schemata(self.context))
                    # value = getattr(context, name).__class__.__name__
                except AttributeError:
                    continue
                if value is field.missing_value:
                    continue

                field_type = field.__class__.__name__

                if field_type in ('RichText',):
                    # TODO: content_type missing
                    value = unicode(value.raw)

                elif field_type in (
                    'NamedImage',
                    'NamedBlobImage',
                    'NamedFile',
                    'NamedBlobFile'
                ):
                    # still to test above with NamedFile & NamedBlobFile
                    fieldname = unicode('_datafield_' + fieldname)

                    if hasattr(value, 'open'):
                        data = value.open().read()
                    else:
                        data = value.data

                    try:
                        max_filesize = int(
                            os.environ.get('JSONIFY_MAX_FILESIZE', 20000000))
                    except ValueError:
                        max_filesize = 20000000

                    if data and len(data) > max_filesize:
                        continue

                    import base64
                    ctype = value.contentType
                    size = value.getSize()
                    dvalue = {
                        'data': base64.b64encode(data),
                        'size': size,
                        'filename': value.filename or '',
                        'content_type': ctype,
                        'encoding': 'base64'
                    }
                    value = dvalue

                elif field_type == 'GeolocationField':
                    # super special plone.formwidget.geolocation case
                    self['latitude'] = getattr(value, 'latitude', 0)
                    self['longitude'] = getattr(value, 'longitude', 0)
                    continue

                elif isinstance(value, date):
                    value = value.isoformat()

                # elif field_type in ('TextLine',):
                else:
                    BASIC_TYPES = (
                        unicode, int, long, float, bool, type(None),
                        list, tuple, dict
                    )
                    if type(value) in BASIC_TYPES:
                        pass
                    else:
                        # E.g. DateTime or datetime are nicely representated
                        value = unicode(value)

                self[unicode(fieldname)] = value

    def _get_at_field_value(self, field):
        if field.accessor is not None:
            return getattr(self.context, field.accessor)()
        return field.get(self.context)

    def get_archetypes_fields(self):
        """If Archetypes is used then dump schema.
        """
        try:
            from Products.Archetypes.interfaces import IBaseObject
            if not self.providedBy(IBaseObject, self.context):
                return
        except:
            return

        try:
            from archetypes.schemaextender.interfaces import IExtensionField
        except:
            IExtensionField = None

        import base64

        fields = []
        for schemata in self.context.Schemata().values():
            fields.extend(schemata.fields())

        for field in fields:
            fieldname = unicode(field.__name__)
            type_ = field.__class__.__name__

            try:
                if self.providedBy(IExtensionField, field):
                    # archetypes.schemaextender case:
                    # Try to get the base class of the schemaexter-field, which
                    # is not an extension field.
                    type_ = [
                        it.__name__ for it in field.__class__.__bases__
                        if not IExtensionField.implementedBy(it)
                    ][0]
            except:
                pass

            fieldnames = [
                'BooleanField',
                'ComputedField',
                'DataGridField',
                'EmailField',
                'FixedPointField',
                'FloatField',
                'IntegerField',
                'LinesField',
                'SimpleDataGridField',
                'StringField',
                'TALESLines',
                'TALESString',
                'TextField',
                'ZPTField',
            ]

            if type_ in fieldnames:
                try:
                    value = field.getRaw(self.context)
                except AttributeError:
                    value = self._get_at_field_value(field)

                if callable(value):
                    value = value()

                if value and type_ in ['ComputedField']:
                    if isinstance(value, str):
                        value = self.decode(value)

                if value and type_ in ['StringField', 'TextField']:
                    try:
                        value = self.decode(value)
                    except AttributeError:
                        # maybe an int?
                        value = unicode(value)
                    except Exception, e:
                        raise Exception('problems with %s: %s' % (
                            self.context.absolute_url(), str(e))
                        )
                elif value and type_ == 'DataGridField':
                    for i, row in enumerate(value):
                        for col_key in row.keys():
                            col_value = row[col_key]
                            if type(col_value) in (unicode, str):
                                value[i][col_key] = self.decode(col_value)

                self[unicode(fieldname)] = value

                if value and type_ in ['StringField', 'TextField']:
                    try:
                        ct = field.getContentType(self.context)
                        self[unicode('_content_type_') + fieldname] = ct
                    except AttributeError:
                        pass

            elif type_ in ['DateTimeField', ]:
                value = str(self._get_at_field_value(field))
                if value:
                    self[unicode(fieldname)] = value

            elif type_ in [
                'ImageField',
                'FileField',
                'BlobField',
                'AttachmentField',
                'ExtensionBlobField',
            ]:
                fieldname = unicode('_datafield_' + fieldname)
                value = self._get_at_field_value(field)
                value2 = value

                if not isinstance(value, str):
                    if isinstance(value.data, str):
                        value = base64.b64encode(value.data)
                    else:
                        data = value.data
                        value = ''
                        while data is not None:
                            value += data.data
                            data = data.next
                        value = base64.b64encode(value)

                try:
                    max_filesize = int(
                        os.environ.get('JSONIFY_MAX_FILESIZE', 20000000)
                    )
                except ValueError:
                    max_filesize = 20000000

                if value and len(value) < max_filesize:
                    size = value2.getSize()
                    try:
                        fname = field.getFilename(self.context)
                    except AttributeError:
                        fname = value2.getFilename()

                    try:
                        fname = self.decode(fname)
                    except AttributeError:
                        # maybe an int?
                        fname = unicode(fname)
                    except Exception, e:
                        raise Exception(
                            'problems with %s: %s' % (
                                self.context.absolute_url(), str(e)
                            )
                        )

                    try:
                        ctype = field.getContentType(self.context)
                    except AttributeError:
                        ctype = value2.getContentType()

                    self[fieldname] = {
                        'data': value,
                        'size': size,
                        'filename': fname or '',
                        'content_type': ctype,
                        'encoding': 'base64'
                    }

            elif type_ in [
                'ReferenceField',
            ]:
                # If there are references, add the UIDs to the referenced
                # contents
                value = field.getRaw(self.context)
                if value:
                    self[fieldname] = value

            elif type_ in ['QueryField']:
                value = field.getRaw(self.context)
                self[fieldname] = [dict(q) for q in value]

            elif type_ in [
                'RecordsField',  # from Products.ATExtensions
                'RecordField',
                'FormattableNamesField',
                'FormattableNameField'
            ]:
                # ATExtensions fields
                # convert items to real dicts
                # value = [dict(it) for it in field.get(self.context)]

                def _enc(val):
                    if type(val) in (unicode, str):
                        val = self.decode(val)
                    return val

                value = []
                for it in field.get(self.context):
                    it = dict(it)
                    val_ = {}
                    for k_, v_ in it.items():
                        val_[_enc(k_)] = _enc(v_)
                    value.append(val_)

                self[unicode(fieldname)] = value

            else:
                # Just try to stringify value
                self[unicode(fieldname)] = unicode(value)

    def get_references(self):
        """AT references.
        """
        try:
            from Products.Archetypes.interfaces import IReferenceable
            if not self.providedBy(IReferenceable, self.context):
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
                    self['_atrefs'][rel].append(
                        '/'.join(ref.getPhysicalPath()))
        brelationships = self.context.getBRelationships()
        for brel in brelationships:
            self['_atbrefs'][brel] = []
            brefs = self.context.getBRefs(relationship=brel)
            for bref in brefs:
                if bref is not None:
                    self['_atbrefs'][brel].append(
                        '/'.join(bref.getPhysicalPath()))

    def get_uid(self):
        """Unique ID of object
        Example::
            {'_uid': '12jk3h1kj23h123jkh13kj1k23jh1'}
        """
        if hasattr(self._context, 'UID'):
            self['_uid'] = self.context.UID()

    def get_id(self):
        """Object id
        :keys: _id
        """
        self['_id'] = self.context.getId()

    def get_path(self):
        """Path of object
        Example::
            {'_path': '/Plone/first-page'}
        """
        self['_path'] = '/'.join(self.context.getPhysicalPath())

    def get_type(self):
        """Portal type of object
        Example::
            {'_type': 'Document'}
        """
        try:
            self['_type'] = self.context.portal_type
        except AttributeError:
            pass

    def get_classname(self):
        """Classname of object.
        Sometimes in old Plone sites we dont know exactly which type we are
        using.
        Example::
           {'_classname': 'ATDocument'}
        """
        self['_classname'] = self.context.__class__.__name__

    def get_properties(self):
        """Object properties
        :keys: _properties
        """
        self['_properties'] = []
        if getattr(self.context, 'propertyIds', False):
            for pid in self.context.propertyIds():
                val = self.context.getProperty(pid)
                typ = self.context.getPropertyType(pid)
                if typ == 'string' and isinstance(val, str):
                    val = self.decode(val)
                if isinstance(val, DateTime)\
                        or isinstance(val, datetime.time)\
                        or isinstance(val, datetime.datetime)\
                        or isinstance(val, datetime.date):
                    val = unicode(val)
                self['_properties'].append(
                    (pid, val, self.context.getPropertyType(pid))
                )

    def get_directly_provided_interfaces(self):
        try:
            from zope.interface import directlyProvidedBy
        except:
            return
        self['_directly_provided'] = [
            it.__identifier__ for it in directlyProvidedBy(self.context)
        ]

    def get_defaultview(self):
        """Default view of object
        :keys: _layout, _defaultpage
        """
        try:
            # When migrating Zope folders to Plone folders
            # set defaultpage to "index_html"
            from Products.CMFCore.PortalFolder import PortalFolder
            if isinstance(self.context, PortalFolder):
                self['_defaultpage'] = 'index_html'
                return
        except:
            pass

        _default = ''
        try:
            _default = '/'.join(
                self.portal_utils.browserDefault(self.context)[1])
        except AttributeError:
            pass

        _layout = ''
        try:
            _layout = self.context.getLayout()
        except:
            pass

        if _default and _layout and _default == _layout:
            # browserDefault always returns the layout, but we only want to set
            # the defaultpage, if it's different from the layout
            _default = ''

        self['_defaultpage'] = _default
        self['_layout'] = _layout

    def get_format(self):
        """Format of object
        :keys: _format
        """
        try:
            self['_content_type'] = self.context.Format()
        except:
            pass

    def get_local_roles(self):
        """Local roles of object
        :keys: _ac_local_roles
        """
        self['_ac_local_roles'] = {}
        if getattr(self.context, '__ac_local_roles__', False):
            for key, val in self.context.__ac_local_roles__.items():
                if key is not None:
                    self['_ac_local_roles'][key] = val

    def get_userdefined_roles(self):
        """User defined roles for object (via sharing UI)
        :keys: _userdefined_roles
        """
        self['_userdefined_roles'] = ()
        if getattr(self.context, 'userdefined_roles', False):
            self['_userdefined_roles'] = self.context.userdefined_roles()

    def get_permissions(self):
        """Permission of object (Security tab in ZMI)
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
                        role_idx = role['name'].index('r') + 1
                        role_name = roles[int(role['name'][role_idx:])]
                        new_roles.append(role_name)
                if unchecked or new_roles:
                    self['_permissions'][perm['name']] = {
                        'acquire': not unchecked,
                        'roles': new_roles
                    }

    def get_owner(self):
        """Object owner
        :keys: _owner
        """
        try:
            try:
                try:
                    self['_owner'] = self.context.getWrappedOwner().getId()
                except:
                    self['_owner'] = self.context.getOwner(info=1).getId()
            except:
                self['_owner'] = self.context.getOwner(info=1)[1]
        except:
            pass

    def get_workflowhistory(self):
        """Workflow history
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
                        workflow_history[w][i]['time'] = str(
                            workflow_history[w][i]['time'])
                    if 'comments' in workflow_history[w][i].keys():
                        workflow_history[w][i]['comments'] =\
                            self.decode(workflow_history[w][i]['comments'])
            self['_workflow_history'] = workflow_history

    def get_position_in_parent(self):
        """Get position in parent
        :keys: _gopip
        """
        try:
            from Products.CMFPlone.CatalogTool import getObjPositionInParent
        except ImportError:
            return

        pos = getObjPositionInParent(self.context)

        # After plone 3.3 the above method returns a 'DelegatingIndexer' rather
        # than an int
        try:
            from plone.indexer.interfaces import IIndexer
            if self.providedBy(IIndexer, pos):
                self['_gopip'] = pos()
                return
        except ImportError:
            pass

        self['_gopip'] = pos

    def get_translation(self):
        """Get LinguaPlone translation linking information.
        """
        if not hasattr(self._context, 'getCanonical'):
            return
        self['_translationOf'] = '/'.join(
            self.context.getCanonical().getPhysicalPath()
        )[len(self.portal_path):]
        self['_canonicalTranslation'] = self.context.isCanonical()

    def _is_cmf_only_obj(self):
        """Test, if a content item is a CMF only object.
        """
        context = self.context
        try:
            from Products.ATContentTypes.interface.interfaces import IATContentType  # noqa
            if self.providedBy(IATContentType, context):
                return False
        except:
            pass
        try:
            from Products.ATContentTypes.interfaces import IATContentType
            if self.providedBy(IATContentType, context):
                return False
        except:
            pass
        try:
            from plone.dexterity.interfaces import IDexterityContent
            if self.providedBy(IDexterityContent, context):
                return False
        except:
            pass
        try:
            from Products.CMFCore.DynamicType import DynamicType
            # restrict this to non archetypes/dexterity
            if isinstance(context, DynamicType):
                return True
        except:
            pass
        return False

    def get_zope_dublin_core(self):
        """If CMFCore is used in an old Zope site, then dump the
        Dublin Core fields
        """
        if not self._is_cmf_only_obj():
            return

        # strings
        for field in ('title', 'description', 'rights', 'language'):
            val = getattr(self.context, field, False)
            if val:
                self[field] = self.decode(val)
            else:
                self[field] = ''
        # tuples
        for field in ('subject', 'contributors'):
            self[field] = []
            val_tuple = getattr(self.context, field, False)
            if val_tuple:
                for val in val_tuple:
                    self[field].append(self.decode(val))
                self[field] = tuple(self[field])
            else:
                self[field] = ()
        # datetime fields
        for field in ['creation_date', 'expiration_date',
                      'effective_date', 'expirationDate', 'effectiveDate']:
            val = getattr(self.context, field, False)
            if val:
                self[field] = str(val)
            else:
                self[field] = ''
        # modification_date:
        # bobobase_modification_time seems to have better data than
        # modification_date in Zope 2.6.4 - 2.9.7
        val = self.context.bobobase_modification_time()
        if val:
            self['modification_date'] = str(val)
        else:
            self['modification_date'] = ''

    def get_zope_cmfcore_fields(self):
        """If CMFCore is used in an old Zope site, then dump the fields we know
        about.
        """
        if not self._is_cmf_only_obj():
            return

        self['_cmfcore_marker'] = 'yes'

        # For Link & Favourite types - field name has changed in Archetypes &
        # Dexterity
        if hasattr(self.context, 'remote_url'):
            self['remoteUrl'] = self.decode(
                getattr(
                    self.context,
                    'remote_url'))

        # For Document & News items
        if hasattr(self.context, 'text'):
            self['text'] = self.decode(getattr(self.context, 'text'))
        if hasattr(self.context, 'text_format'):
            self['text_format'] = self.decode(
                getattr(
                    self.context,
                    'text_format'))

        # Found in Document & News items, but not sure if this is necessary
        if hasattr(self.context, 'safety_belt'):
            self['safety_belt'] = self.decode(
                getattr(
                    self.context,
                    'safety_belt'))

        # Found in File & Image types, but not sure if this is necessary
        if hasattr(self.context, 'precondition'):
            self['precondition'] = self.decode(
                getattr(
                    self.context,
                    'precondition'))

        data_type = self.context.portal_type

        if data_type in ['File', 'Image']:
            fieldname = unicode('_datafield_%s' % data_type.lower())
            value = self.context
            orig_value = value

            if not isinstance(value, str):
                try:
                    from base64 import b64encode
                except:
                    # Legacy version of base64 (eg on Python 2.2)
                    from base64 import encodestring as b64encode
                if isinstance(value.data, str):
                    value = b64encode(value.data)
                else:
                    data = value.data
                    value = ''
                    while data is not None:
                        value += data.data
                        data = data.next
                    value = b64encode(value)

            try:
                max_filesize = int(
                    os.environ.get(
                        'JSONIFY_MAX_FILESIZE',
                        20000000))
            except ValueError:
                max_filesize = 20000000

            if value and len(value) < max_filesize:
                size = orig_value.getSize()
                fname = orig_value.getId()
                try:
                    fname = self.decode(fname)
                except AttributeError:
                    # maybe an int?
                    fname = unicode(fname)
                except Exception, e:
                    raise Exception('problems with %s: %s' %
                                    (self.context.absolute_url(), str(e)))

                ctype = orig_value.getContentType()
                self[fieldname] = {
                    'data': value,
                    'size': size,
                    'filename': fname or '',
                    'content_type': ctype,
                    'encoding': 'base64'
                }

    def get_zopeobject_document_src(self):
        if not self._is_cmf_only_obj():
            return
        document_src = getattr(self.context, 'document_src', None)
        if document_src:
            self['document_src'] = self.decode(document_src())
        else:
            self['_zopeobject_document_src'] = ''
