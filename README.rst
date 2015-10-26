``collective.jsonify`` exports your Plone content to JSON_.

Many packages that export data from Plone have complicated dependencies, and so
only work with Plone 3.0 or higher (or not even with 3.0).
``collective.jsonify``'s only dependency is simplejson_. It can be installed in
any Plone version as far back as:

- Plone 2.1 (or probably even Plone 2.0, but not tested)
- Zope 2.6.4 (with CMF rather than Plone)
- Python 2.2

The exported JSON_ is a collective.transmogrifier_ friendly format. Install
``collective.jsonify`` on a site you want to export from, and setup an import
transmogrifier pipeline on the site you're importing to, using the blueprints in
the collective.jsonmigrator_ package.

Alternatively use the provided export script by adding it to an external method as described in `using the exporter`_.

For more information see the documentation_.


:Warning: This product may contain traces of nuts.
:Author: `Rok Garbas`_, *migrating for you since 2008*
:Source: http://github.com/collective/collective.jsonify


.. _`simplejson`: http://pypi.python.org/simplejson
.. _`JSON`: http://en.wikipedia.org/wiki/JSON
.. _`collective.transmogrifier`: http://pypi.python.org/pypi/collective.transmogrifier
.. _`collective.jsonmigrator`: http://pypi.python.org/pypi/collective.jsonmigrator
.. _`using the exporter`: https://collectivejsonify.readthedocs.org/en/latest/#using-the-exporter
.. _`documentation`: https://collectivejsonify.readthedocs.org
.. _`Rok Garbas`: http://www.garbas.si/labs/plone-migration
