``collective.jsonify`` exports your Plone content to JSON_.

Many packages that export data from Plone have complicated dependencies, and so
only work with Plone 3.0 or higher (or not even with 3.0).
``collective.jsonify``'s only dependency is simplejson_. It can be installed in
any Plone version as far back as:

- Plone 2.1 (or probably even Plone 2.0, but not tested)
- Zope 2.6.4 (with CMF rather than Plone)
- Python 2.2

You can use the provided export script by adding it to an external method as described below.

The exported json is a collective.transmogrifier_ friendly format. Install
``collective.jsonify`` on a site you want to export from, and setup an import
transmogrifier pipeline on the site you're importing to, using the blueprints in
the collective.jsonmigrator_ package.

Alternatively you can use collective.exportimport_ to
import that data as described in https://github.com/collective/collective.exportimport#migrate-very-old-plone-versions-with-data-created-by-collective-jsonify


How to install it
=================

Install ``collective.jsonify`` for your Plone site, so that it is available in
your Plone site's ``PYTHONPATH``, including the ``simplejson`` package. The
easiest way is to use buildout, as for any other modern Plone project. Other
options include:

1. Play with PYTHONPATH manually.
2. Use ``easy_install collective.jsonify`` or ``pip install collective.jsonify`` which
   will also pull ``simplejson``.

*Note: if you are working with python 2.2, then you will need to install a `tweaked
branch of simplejson <https://github.com/simplejson/simplejson/tree/python2.2>`_.*


Then run your Zope instance, go to the Zope root and create the necessary
External Methods.

External method for exporting JSON files to the filesystem:

 - export_content:
   - id: ``export_content``
   - module name: ``collective.jsonify.json_methods``
   - function name: ``export_content``


External methods for remote access from the importing Plone instance, using
``collective.jsonmigrator``:

 - get_item
   - id: ``get_item``
   - module name: ``collective.jsonify.json_methods``
   - function name: ``get_item``

 - get_children:
   - id: ``get_children``
   - module name: ``collective.jsonify.json_methods``
   - function name: ``get_children``

 - get_catalog_results:
   - id: ``get_catalog_results``
   - module name: ``collective.jsonify.json_methods``
   - function name: ``get_catalog_results``


It's true that External Methods are not the nicest to work with and using them
makes the setup a little long. But the nice thing about External Methods is that
they work in Plone 1.0 as well as in Plone 4.0, so you could potentially use
``collective.jsonify`` to migrate from very old Plone versions.


How to use it
=============

``collective.jsonify`` is intended to be used in conjunction with
``collective.jsonmigrator``. There you can find an example transmogrifier
pipeline that connects to the Plone site running ``collective.jsonify``, crawls
it, extracts the content and imports it into the target site.

To see what ``collective.jsonmigrator`` is actually seeing you can issue "json
views" on content you want to explore::

    http://localhost:8080/Plone/front-page/get_item
    http://localhost:8080/Plone/front-page/get_children

The first gets all content out of ``front-page``; the second lists all content
contained inside this object and returns their ids.

Finally, you can use ``get_catalog_results`` to catalog query results as a list
of paths. To use it, you need to hand your query as a base64'ed Python dict
string. Here's an example of doing this with curl::

    curl --data catalog_query=$(echo '{"Type": "Slide"}' | base64 -w0) \
      'http://localhost:8080/Plone/portal_catalog/get_catalog_results


Using the exporter
==================

To export your site to a directory of JSON files use the ``collective.jsonify.export.export_content`` function.

This is how to use it with an external method:

- Install ``collective.jsonify`` for your instance.

- Create a script in your Zope instance ``Extensions`` directory, e.g. in ``BUILDOUT_ROOT/parts/instance/Extensions``.
  Create the ``Extensions`` directory, if it doesn't exist.
  Create a file ``json_methods.py`` with the following contents - adapt for your needs::

    from collective.jsonify.export import export_content as export_content_orig


    def export_content(self):
        return export_content_orig(
            self,
            basedir='/tmp',  # export directory
            extra_skip_classname=['ATTopic'],
            # batch_start=5000,
            # batch_size=5000,
            # batch_previous_path='/Plone/last/exported/path'  # optional, but saves more memory because no item has to be jsonified before continuing...
        )

- Create the "External Method" in the ZMI at the Zope root or Plone root.
  id: "export_content"
  module name: "json_methods"
  function name: "export_content"

   For more info on "External Methods" see: https://zope.readthedocs.io/en/latest/zopebook/ScriptingZope.html#using-external-methods

- To start the export, open the url in your browser::
    http://localhost:8080/Plone/export_content


How to extend it
================

We try to cover the basic Plone types to export useful content out of Plone. We
cannot predict all usecases, but if you have custom requirements it's easy to
extend functionality.

To control what to export before serialzing is the fastest way to extend..
You can override the ``export_content`` "External Methods" as described above.

Example::

    from collective.jsonify.export import export_content as export_content_orig

    EXPORTED_TYPES = [
        "Folder",
        "Document",
        "News Item",
        "Event",
        "Link",
        "Topic",
        "File",
        "Image",
        "RichTopic",
    ]

    EXTRA_SKIP_PATHS = [
        "/Plone/archiv/",
        "/Plone/do-not-import/",
    ]

    # Path from which to continue the export.
    # The export walks the whole site respecting the order.
    # It will ignore everything untill this path is reached.
    PREVIOUS = ""

    def export_content(self):
        return export_content_orig(
            self,
            basedir="/var/lib/zope/json",
            skip_callback=skip_item,
            extra_skip_classname=[],
            extra_skip_id=[],
            extra_skip_paths=EXTRA_SKIP_PATHS,
            batch_start=0,
            batch_size=10000,
            batch_previous_path=PREVIOUS or None,
        )

    def skip_item(item):
        """Return True if the item should be skipped"""
        portal_type = getattr(item, "portal_type", None)
        if portal_type not in EXPORTED_TYPES:
            return True


You can modify or extend the exported data by passing additional wrappers to ``get_item`` or ``export_content``.
These should to be "External Methods"::

    http://localhost:8080/Plone/front-page/get_item?additional_wrappers=extend_item

These hooks take the object and the serialized data as arguments.

Example::

    def extend_item(obj, item):
        """Extend to work better well with collective.exportimport"""
        from Acquisition import aq_parent

        # Info about parent
        parent = aq_parent(obj)
        item["parent"] = {
            "@id": parent.absolute_url(),
            "@type": getattr(parent, "portal_type", None),
        }
        if getattr(parent.aq_base, "UID", None) is not None:
            item["parent"]["UID"] = parent.UID()

        # Review state
        try:
            review_state = obj.portal_workflow.getInfoFor(obj, "review_state")
        except Exception, e:
            review_state = None
        item["review_state"] = review_state

        # Block inheritance of local roles
        item["_ac_local_roles_block"] = getattr(obj.aq_base, "__ac_local_roles_block__", False)

        return item


.. _`simplejson`: http://pypi.python.org/simplejson
.. _`JSON`: http://en.wikipedia.org/wiki/JSON
.. _`collective.transmogrifier`: http://pypi.python.org/pypi/collective.transmogrifier
.. _`collective.jsonmigrator`: http://pypi.python.org/pypi/collective.jsonmigrator
.. _`collective.exportimport`: https://github.com/collective/collective.exportimport
