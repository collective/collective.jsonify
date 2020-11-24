# Run collective.jsonify migration export
# Usage
# complete site: bin/zeoclient run scripts/migration-export.py
# subfolder:     bin/zeoclient run scripts/migration-export.py  path/to/folder

import sys

from zope.component.hooks import setSite



if len(sys.argv) == 4:
    site = app.restrictedTraverse(sys.argv[-1])
else:
    print('You must specify the id of the Plone site')
    sys.exit(0)

setSite(site)
view = getattr(site, 'export_content')
view()

print('DONE')
