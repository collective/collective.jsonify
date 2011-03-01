"""
These wrappers get the data in a format that can be used by
the atschemaupdater blueprint from plone.app.transmogrifier
and the atdatafield bluprint from this same package.
"""

import base64

from base_wrapper import BaseWrapper


class DocumentWrapper(BaseWrapper):

    def __init__(self, obj):
        super(DocumentWrapper, self).__init__(obj)
        self['text'] = self.obj.text.decode(self.charset, 'ignore')


class LinkWrapper(BaseWrapper):

    def __init__(self, obj):
        super(LinkWrapper, self).__init__(obj)
        self['remoteUrl'] = self.obj.remote_url


class NewsItemWrapper(DocumentWrapper):

    def __init__(self, obj):
        super(NewsItemWrapper, self).__init__(obj)
        self['text_format'] = self.obj.text_format


class ListCriteriaWrapper(BaseWrapper):

    def __init__(self, obj):
        super(ListCriteriaWrapper, self).__init__(obj)
        self['field'] = self.obj.field
        self['value'] = self.obj.value
        self['operator'] = self.obj.operator


class StringCriteriaWrapper(BaseWrapper):

    def __init__(self, obj):
        super(StringCriteriaWrapper, self).__init__(obj)
        self['field'] = self.obj.field
        self['value'] = self.obj.value


class SortCriteriaWrapper(BaseWrapper):

    def __init__(self, obj):
        super(SortCriteriaWrapper, self).__init__(obj)
        self['index'] = elf.bj.index
        self['reversed'] = self.obj.reversed


class DateCriteriaWrapper(BaseWrapper):

    def __init__(self, obj):
        super(DateCriteriaWrapper, self).__init__(obj)
        self['field'] = self.obj.field
        self['value'] = self.obj.value
        self['operation'] = self.obj.operation
        self['daterange'] = self.obj.daterange


class FileWrapper(BaseWrapper):

    def __init__(self, obj):
        super(FileWrapper, self).__init__(obj)
        self['_datafield_file'] = base64.b64encode(self.obj.data)


class ImageWrapper(BaseWrapper):

    def __init__(self, obj):
        super(ImageWrapper, self).__init__(obj)
        self['_datafield_image'] = base64.b64encode(self.obj.data)


class EventWrapper(BaseWrapper):

    def __init__(self, obj):
        super(EventWrapper, self).__init__(self.obj)
        self['startDate'] = str(self.obj.start_date)
        self['endDate'] = str(self.obj.end_date)
        self['location'] = self.obj.location.decode(self.charset, 'ignore')
        self['contactName'] = self.obj.contact_name.decode(self.charset, 'ignore')
        self['contactEmail'] = self.obj.contact_email
        self['contactPhone'] = self.obj.contact_phone
        self['eventUrl'] = self.obj.event_url


