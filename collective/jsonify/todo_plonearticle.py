"""These wrapper gets the data for PloneArticles in a format that can be used
by the plone_article blueprint from this same package.
"""
from cmfcontent_wrapper import NewsItemWrapper
import base64


class ArticleWrapper(NewsItemWrapper):

    def __init__(self, obj):
        super(ArticleWrapper, self).__init__(obj)
        try:
            self['cooked_text'] = self.obj.cooked_text.decode(self.charset)
        except UnicodeDecodeError:
            self['cooked_text'] = self.obj.cooked_text.decode('latin-1')

        plonearticle_attachments = []
        for item_id in self.obj.attachments_ids:
            item = obj[item_id]
            plonearticle_attachments.append({
                'id': (item_id, {}),
                'title': (item.title.decode(self.charset, 'ignore'), {}),
                'description': (item.description.decode(
                    self.charset, 'ignore'), {}),
                'attachedFile': [base64.b64encode(item.getFile()), {}],
            })
        self['_plonearticle_attachments'] = plonearticle_attachments

        plonearticle_images = []
        for item_id in self.obj.images_ids:
            item = self.obj[item_id]
            plonearticle_images.append({
                'id': (item_id, {}),
                'title': (item.title.decode(self.charset, 'ignore'), {}),
                'description': (item.description.decode(
                    self.charset, 'ignore'), {}),
                'attachedImage': [base64.b64encode(item.data), {}],
            })
        self['_plonearticle_images'] = plonearticle_images
