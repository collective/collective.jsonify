from AccessControl import Unauthorized
from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
import os

SCHEMAEXTENDER_FIELDS = ['BaseExtensionField', 'TranslatableExtensionField']


class Wrapper(dict):
    """ Gets the data in a format that can be used by the
        transmogrifier blueprints in collective.jsonmigrator
    """

    def __init__(self, context):

        self.context = context
        self._context = aq_base(context)
        self.portal = getToolByName(self.context, 'portal_url').getPortalObject()
        self.pr = self.portal.portal_repository
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
        if getattr(self.context, 'get_local_roles', False):
            for key, val in self.context.get_local_roles():
                if key is not None:
                    self['_local_roles'][key] = val

    def get_local_roles_block(self):
        self['_local_roles_block'] = getattr(
            self.context, '__ac_local_roles_block__', False)

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

	# Does not work on old plone
        #from Products.CMFPlone.CatalogTool import getObjPositionInParent
        #pos = getObjPositionInParent(self.context) 
        
        # Hack for old plone
        try:
            pos = self.context.aq_parent.getObjectPosition(self.context.id)
        except:
            pos = 10000

        # After plone 3.3 the above method returns a 'DelegatingIndexer' rather than an int
        try:
            from plone.indexer.interfaces import IIndexer
            if IIndexer.isImplementedBy(pos):
                self['_gopip'] = pos()
                return
        except ImportError:
            pass
            
        self['_gopip'] = pos

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

    def get_dexterity_fields(self):
        """ If dexterity is used then extract fields
        """
        try:
            from plone.dexterity.utils import iterSchemata
            #from plone.uuid.interfaces import IUUID
            from zope.schema import getFieldsInOrder
            from datetime import datetime
            from plone.directives import form
            
            if not form.Schema.isImplementedBy(self.context):
                return

        except:
            return

        #get all fields for this obj
        for schemata in iterSchemata(self.context):
            for fieldname, field in getFieldsInOrder(schemata):
                try:
                    value = field.get(schemata(self.context))
                    #value = getattr(context, name).__class__.__name__ 
                except AttributeError:
                    continue
                if value is field.missing_value:
                    continue
                
                field_type = field.__class__.__name__ 
                
                if field_type in ('RichText',):
                    value = unicode(value.raw)
                    
                elif field_type in ('NamedImage',):
                    fieldname = unicode('_datafield_' + fieldname)

                    if hasattr(value, 'open'):
                        data = value.open().read()
                    else:
                        data = value.data

                    try:
                        max_filesize = int(os.environ.get('JSONIFY_MAX_FILESIZE', 20000000))
                    except ValueError:
                        max_filesize = 20000000

                    if data and len(data) > max_filesize:
                        continue
                        
                    import base64
                    ctype = value.contentType
                    size = value.getSize()
                    dvalue = {
                        'data': base64.encodestring(data),
                        'size': size,
                        'filename': value.filename or '',
                        'content_type': ctype}                    
                    value = dvalue

                elif field_type in ('DateTime',):
                    if isinstance(value, basestring):
                        value = datetime.strptime(value, '%Y-%m-%d')
                    if isinstance(value, datetime):
                        value = value.date()

                #elif field_type in ('TextLine',):
                else:
                    BASIC_TYPES = (unicode, int, long, float, bool, type(None))
                    if type(value) in BASIC_TYPES:
                        pass
                    elif self.field is not None:
                        value = unicode(value)
                    else:
                        raise ValueError('Unable to serialize field value')                

                self[unicode(fieldname)] = value

    def get_archetypes_fields(self):
        """ If Archetypes is used then dump schema
        """
        try:
            from Products.Archetypes.interfaces.base import IBaseObject
            if not IBaseObject.isImplementedBy(self.context):
                return
        except:
            return

        import base64
        try:
            import archetypes.schemaextender
            fields = self.context.Schema().fields()
        except ImportError:
            fields = self.context.schema.fields()

        for field in fields:
            fieldname = unicode(field.__name__)
            type_ = field.__class__.__name__

            if field not in self.context.schema.fields():
                for klass in field.__class__.__bases__:
                    if klass.__name__ not in SCHEMAEXTENDER_FIELDS:
                        type_ = klass.__name__
                        break

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
                        value = base64.encodestring(value.data)
                    else:
                        data = value.data
                        value = ''
                        while data is not None:
                            value += data.data
                            data = data.next
                        value = base64.encodestring(value)

                try:
                    max_filesize = int(os.environ.get('JSONIFY_MAX_FILESIZE', 20000000))
                except ValueError:
                    max_filesize = 20000000

                if value and len(value) < max_filesize:
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

                def get_file_data(obj):
                    value = field.get(obj)
                    size = 0

                    if type(value) is not str:
                        size = value.getSize()
                        if type(value.data) is str:
                            value = base64.b64encode(value.data)
                        else:
                            data = value.data
                            value = ''
                            while data is not None:
                                value += data.data
                                data = data.next
                            value = base64.b64encode(value)
                    return value, size

                # Check if there are multiple versions
                try:
                    history = self.pr.getHistory(self.context, oldestFirst=True)
                except Unauthorized, e:
                    history = []

                if history:
                    versions = []
                    for version in history:
                        value, size = get_file_data(version.object)
                        fname = field.getFilename(version.object)
                        ctype = field.getContentType(version.object)

                        versions.append({
                            'version_id': version.version_id,
                            'version_sysmetadata': version.sys_metadata,
                            'data': value,
                            'size': size,
                            'filename': fname,
                            'content_type': ctype,
                        })

                    # Include working copy if it is not saved as a version
                    version_id = getattr(self.context, "version_id", None)
                    if not self.pr.isUpToDate(self.context, version_id):
                        value, size = get_file_data(self.context)
                        fname = field.getFilename(self.context)
                        ctype = field.getContentType(self.context)
                        versions.append({
                            'version_id': 'WORKING_COPY',
                            'data': value,
                            'size': size,
                            'filename': fname,
                            'content_type': ctype,
                        })

                    self[fieldname] = versions

                else:
                    value, size = get_file_data(self.context)
                    fname = field.getFilename(self.context)
                    ctype = field.getContentType(self.context)
                    self[fieldname] = {
                        'data': value,
                        'size': size,
                        'filename': fname,
                        'content_type': ctype,
                    }

            elif type_ in ['ReferenceField', 'ObjectTransitionField']:
                pass

            elif type_ in ['ComputedField']:
                continue

            else:
                raise TypeError('Unknown field type (%s) for ArchetypesWrapper in '
                        '%s in %s' % (fieldname, self.context.absolute_url()))

    def get_references(self):
        """ AT references
        """
        try:
            from Products.Archetypes.interfaces.base import IReferenceable
            if not IReferenceable.isImplementedBy(self.context):
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


class WrapperWithoutFile(Wrapper):

    def get_archetypes_fields(self):

        """ If Archetypes is used then dump schema
        """

        try:
            from Products.Archetypes.interfaces import IBaseObject
            if not IBaseObject.providedBy(self.context):
                return
        except:
            return

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

            elif type_ in ['ReferenceField', 'ObjectTransitionField']:
                pass

            elif type_ in ['ComputedField']:
                continue

            else:
                raise TypeError('Unknown field type for ArchetypesWrapper in '
                        '%s in %s' % (fieldname, self.context.absolute_url()))


class DiscussionItemWrapper(Wrapper):
    """Gets the Discussion Item specific attributes in a format
    that can be used by the blueprints in collective.jsonmigrator"""

    def __init__(self, context):
        self.context = context
        self._context = aq_base(context)
        self.portal = getToolByName(
            self.context, 'portal_url').getPortalObject()
        self.pr = self.portal.portal_repository
        self.portal_path = '/'.join(self.portal.getPhysicalPath())
        self.portal_utils = getToolByName(self.context, 'plone_utils')
        self.charset = self.portal.portal_properties.site_properties.default_charset
        # newer seen it missing ... but users can change it
        if not self.charset:
            self.charset = 'utf-8'

        for method in dir(self):
            if method.startswith('get_'):
                getattr(self, method)()

    def get_discusionitem_attributes(self):
        """Return all specific attributes used for the Migration
        of Plone Discussion Items."""

        self['in_reply_to'] = self.context.in_reply_to
        self['id'] = self.context.id
        self['title'] = self.context.title
        self['text'] = self.context.text
        self['cooked_text'] = self.context.cooked_text
        self['text_format'] = self.context.text_format
        self['creation_date'] = str(self.context.creation_date)
        self['modification_date'] = str(self.context.modification_date)
        self['expiration_date'] = str(self.context.expiration_date)
        self['creator'] = self.context.Creator()
