import os
import os.path
import json
from Products.CMFPlone.interfaces import IPloneSiteRoot
from collective.jsonify import export
from collective.jsonify.export import export_content
from zope.component.hooks import setSite


def jsonify(context, request):
    app = context
    basedir = os.environ.get('JSONIFYDIR', None)
    if basedir:
        basedir = os.path.abspath(basedir)
        kwargs = dict(basedir=basedir)
    else:
        kwargs = dict()
    sites = dict()
    for obj in app.values():
        if IPloneSiteRoot.providedBy(obj):
            setSite(obj)
            export_content(obj, **kwargs)
            sites[obj.getId()] = os.path.basename(export.TMPDIR)
    if basedir:
        sites_filename = os.path.join(basedir, 'sites.json')
        with open(sites_filename, 'w') as sites_file:
            json.dump(sites, sites_file)
