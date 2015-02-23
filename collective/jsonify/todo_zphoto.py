"""These wrappers get the data in a format that can be used by the
atschemaupdater blueprint from plone.app.transmogrifier and the atdatafield
bluprint from this same package.
"""
from base_wrapper import BaseWrapper


class ZPhotoWrapper(BaseWrapper):

    def __init__(self, obj):
        super(ZPhotoWrapper, self).__init__(obj)
        self['show_exif'] = self.obj.show_exif
        self['exif'] = self.obj.exif
        self['iptc'] = self.obj.iptc
        self['path'] = self.obj.path
        self['dir'] = self.obj.dir
        self['filename'] = self.obj.filename
        # self['_thumbs'] = obj._thumbs
        self['dict_info'] = self.obj.dict_info
        self['format'] = self.obj.format
        self['tmpdir'] = self.obj.tmpdir
        self['backup'] = self.obj.backup


class ZPhotoSlidesWrapper(BaseWrapper):

    def __init__(self, obj):
        super(ZPhotoSlidesWrapper, self).__init__(obj)
        try:
            self['update_date'] = str(self.obj.update_date)
            self['show_postcard'] = self.obj.show_postcard
            self['show_ARpostcard'] = self.obj.show_ARpostcard
            self['show_rating'] = self.obj.show_rating
            self['size'] = self.obj.size
            self['max_size'] = self.obj.max_size
            self['sort_field'] = self.obj.sort_field
            self['allow_export'] = self.obj.allow_export
            self['show_export'] = self.obj.show_export
            # self['visits_log'] = obj.visits_log
            self['non_hidden_pic'] = self.obj.non_hidden_pic
            self['list_non_hidden_pic'] = self.obj.list_non_hidden_pic
            self['rows'] = self.obj.rows
            self['column'] = self.obj.column
            self['zphoto_header'] = self.obj.zphoto_header
            self['list_photo'] = self.obj.list_photo
            self['zphoto_footer'] = self.obj.zphoto_footer
            self['symbolic_photo'] = self.obj.symbolic_photo
            self['keywords'] = self.obj.keywords
            self['first_big'] = self.obj.first_big
            self['show_automatic_slide_show'] =\
                self.obj.show_automatic_slide_show
            self['show_viewed'] = self.obj.show_viewed
            self['show_exif'] = self.obj.show_exif
            self['photo_space'] = self.obj.photo_space
            self['last_modif'] = str(self.obj.last_modif)
            self['show_iptc'] = self.obj.show_iptc
            self['formats_available'] = self.obj.formats_available
            self['default_photo_size'] = self.obj.default_photo_size
            self['formats'] = self.obj.formats
            self['actual_css'] = self.obj.actual_css
            self['thumb_width'] = self.obj.thumb_width
            self['thumb_height'] = self.obj.thumb_height
            # self['list_rating'] = obj.list_rating
            self['photo_folder'] = self.obj.photo_folder
            self['tmpdir'] = self.obj.tmpdir
            self['lib'] = self.obj.lib
            self['convert'] = self.obj.convert
            self['use_http_cache'] = self.obj.use_http_cache
        except Exception, e:
            raise Exception(
                'Problems with %s: %s' %
                (self.obj.absolute_url(), str(e)))
