
import base64
from collective.plone2x_jsonify.base import DCWrapper


class ArchetypesWrapper(DCWrapper):
    """
    This gets data to be used with the
    atschemaupdater blueprint from plone.app.transmogrifier and
    the atdatafield blueprint in this package.
    """

    def __init__(self, obj):
        super(ArchetypesWrapper, self).__init__(obj)

        fields = self.obj.schema.fields()
        for field in fields:
            fieldname = unicode(field.__name__)
            type_ = field.__class__.__name__
            if type_ in ['StringField', 'BooleanField', 'LinesField', 'IntegerField', 'TextField',
                         'SimpleDataGridField', 'FloatField', 'FixedPointField',
                         'TALESString', 'TALESLines', 'ZPTField']:
                try:
                    value = field.getRaw(obj)
                except AttributeError:
                    value = field.get(obj)
                if callable(value) is True:
                    value = value()
                if value and type_ in ['StringField', 'TextField']:
                    try:
                        value = value.decode(self.charset)
                    except AttributeError:
                        # maybe an int?
                        value = unicode(value)
                    except Exception, e:
                        raise Exception('problems with %s: %s' % (self.obj.absolute_url(), str(e)))
                if value:
                    try:
                        ct = field.getContentType(obj)
                    except AttributeError:
                        ct = ''
                    self[unicode(fieldname)] = value
                    self[unicode('_content_type_')+fieldname] = ct
            elif type_ in ['DateTimeField']:
                value = str(field.get(self.obj))
                if value:
                    self[unicode(fieldname)] = value
            elif type_ in ['ImageField', 'FileField']:
                fieldname = unicode('_datafield_'+fieldname)
                value = field.get(self.obj)
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
                if value and len(value) < 20000000:
                    size = value2.getSize()
                    fname = field.getFilename(obj)
                    try:
                        fname = fname.decode(self.charset, 'ignore')
                    except AttributeError:
                        # maybe an int?
                        fname = unicode(fname)
                    except Exception, e:
                        raise Exception('problems with %s: %s' % (self.obj.absolute_url(), str(e)))
                    ctype = field.getContentType(obj)
                    self[fieldname] = {
                        'data': value,
                        'size': size,
                        'filename': fname or '',
                        'content_type': ctype}
            elif type_ in ['ComputedField', 'ReferenceField']:
                pass
            else:
                raise TypeError('Unknown field type for ArchetypesWrapper in '
                                '%s in %s' % (fieldname, obj.absolute_url()))

            # AT references
            from Products.Archetypes.interfaces import IReferenceable
            if IReferenceable.providedBy(obj):
                self['_atrefs'] = {}
                self['_atbrefs'] = {}
                relationships = obj.getRelationships()
                for rel in relationships:
                    self['_atrefs'][rel] = []
                    refs = obj.getRefs(relationship=rel)
                    for ref in refs:
                        self['_atrefs'][rel].append('/'.join(ref.getPhysicalPath()))
                brelationships = obj.getBRelationships()
                for brel in brelationships:
                    self['_atbrefs'][brel] = []
                    brefs = obj.getBRefs(relationship=brel)
                    for bref in brefs:
                        self['_atbrefs'][brel].append('/'.join(bref.getPhysicalPath()))
