``collective.jsonify`` exports your Plone content to JSON_.

Many packages that export data from Plone have complicated dependencies, and so
only work with Plone 3.0 or higher (or not even with 3.0).
``collective.jsonify``'s only dependency is simplejson_. It can be installed in
any Plone version, probably as far back as Plone 2.0 (not tested!).

The exported JSON_ is a collective.transmogrifier_ friendly format. Install
``collective.jsonify`` on a site you want to export from, and setup an import
transmogrifier pipeline on the site you're importing to, using the blueprints in
the collective.jsonmigrator_ package.

For more information see the documentation_.


:Warning: This product may contain traces of nuts.
:Author: `Rok Garbas`_, *migrating for you since 2008*
:Source: http://github.com/collective/collective.jsonify


.. _`simplejson`: http://pypi.python.org/simplejson
.. _`JSON`: http://en.wikipedia.org/wiki/JSON
.. _`collective.transmogrifier`: http://pypi.python.org/collective.transmogrifier
.. _`collective.jsonmigrator`: http://pypi.python.org/pypi/collective.jsonmigrator
.. _`documentation`: https://collectivejsonify.readthedocs.org
.. _`Rok Garbas`: http://www.garbas.si/labs/plone-migration
