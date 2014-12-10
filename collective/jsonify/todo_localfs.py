"""These wrappers get the data in a format that can be used by the
atschemaupdater blueprint from plone.app.transmogrifier and the atdatafield
bluprint from this same package.
"""
from base_wrapper import BaseWrapper


class LocalFSWrapper(BaseWrapper):

    def __init__(self, obj):
        super(LocalFSWrapper, self).__init__(obj)
        self['basepath'] = self.obj.basepath
