"""These wrappers get the data in a format that can be used by the
atschemaupdater blueprint from plone.app.transmogrifier and the atdatafield
bluprint from this same package.
"""
from atcontent_wrapper import ArchetypesWrapper
from base_wrapper import BaseWrapper


class I18NFolderWrapper(BaseWrapper):

    def __init__(self, obj):
        super(I18NFolderWrapper, self).__init__(obj)
        # We are ignoring another languages
        lang = self.obj.getDefaultLanguage()
        data = self.obj.folder_languages.get(lang, None)
        if data is not None:
            self['title'] = data['title'].decode(self.charset, 'ignore')
            self['description'] = data['description'].decode(
                self.charset,
                'ignore')
        else:
            raise Exception(
                'ERROR: Cannot get default data for I18NFolder "%s"' %
                self['_path'])

        # delete empty title in properties
        for prop in self['_properties']:
            propname, propvalue, proptitle = prop
            if propname == "title":
                self['_properties'].remove(prop)

        # Not lose information: generate properites es_title, en_title, etc.
        for lang in self.obj.folder_languages:
            data = self.obj.folder_languages[lang]
            for field in data:
                self['_properties'].append([
                    '%s_%s' % (lang, field),
                    data[field].decode(self.charset, 'ignore'), 'text'
                ])


class I18NLayerWrapper(ArchetypesWrapper):

    def __init__(self, obj):
        super(I18NLayerWrapper, self).__init__(obj)
        lang = self.obj.portal_properties.site_properties.default_language
        if lang not in self.obj.objectIds():
            raise Exception(
                'ERROR: Cannot get default data for I18NLayer "%s"' %
                self['_path'])
        else:
            real = self.obj[lang]
            self['title'] = real.title.decode(self.charset, 'ignore')
            self['description'] = real.description.decode(
                self.charset,
                'ignore')
            self['text'] = real.text.decode(self.charset, 'ignore')

        # Not lose information: generate properites es_title, en_title, etc.
        # TODO: Export all archetypes, but I don't need now, only document
        # important fields
        for lang, content in self.obj.objectItems():
            data = dict(title=content.title,
                        description=content.description,
                        text=content.text)
            for field in data:
                self['_properties'].append([
                    '%s_%s' % (lang, field),
                    data[field].decode(self.charset, 'ignore'), 'text'
                ])
