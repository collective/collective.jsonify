import os
import os.path
from Products.CMFPlone.interfaces import IPloneSiteRoot
from collective.jsonify.export import export_content
from zope.component.hooks import setSite


def jsonify(context, request):
    app = context
    basedir = os.path.abspath(os.environ.get('JSONIFYDIR', None))
    if basedir:
        kwargs = dict(basedir=basedir)
    else:
        kwargs = dict()
    for obj in app.values():
        if IPloneSiteRoot.providedBy(obj):
            setSite(obj)
            export_content(obj, **kwargs)
