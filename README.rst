
Main reason for this package lays in complicate dependencies in products which
export data from Plone. Normaly the only work with Plone 3.0 or higher (or not
even with 3.0).

Therefore this package provides no major dependency and can be installed in any
Plone version. Probably it should work also for Plone 1.0, but this was not
tested. Only dependency is simplejson_.

Format in which data is exported is JSON_ in collective.transmogrifier_
friendly format. There is also blueprint developed which is laying in
collective.jsonmigrator_ package.

Package is TESTED_ and DOCUMENTED_.


:Warning: This product may contain traces of nuts.
:Author: `Rok Garbas`_, *migrating for you since 2008*
:Source: http://github.com/collective/collective.jsonify


.. _`collective.transmogrifier`: http://pypi.python.org/collective.transmogrifier
.. _`simplejson`: http://pypi.python.org/simplejson
.. _`TESTED`: http://packages.python.org/collective.jsonify/testing.html
.. _`DOCUMENTED`: http://packages.python.org/collective.jsonify
.. _`collective.jsonmigrator`: http://pypi.python.org/pypi/collective.jsonmigrator
.. _`Rok Garbas`: http://www.garbas.si/labs/plone-migration
.. _`JSON`: http://en.wikipedia.org/wiki/JSON
