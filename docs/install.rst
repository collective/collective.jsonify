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

Instead of doing on-the-fly exporting with collective.jsonmigrator, you can
also export your site's content to json files for multiple re-use. This is done
by the export script and the external method, as described above. You can also
batch-export the contents, if you get out of memory on your exporting machine.
Here is an example on how to configure the export script for using as an 
external method::

    from collective.jsonify.export import export_content as export_content_orig


    def export_content(self):
        return export_content_orig(
            self,
            basedir='/tmp',  # export directory
            extra_skip_classname=['ATTopic'],
            batch_start=5000,
            batch_size=5000,
            batch_previous_path='/Plone/last/exported/path'  # optional, but saves more memory because no item has to be jsonified before continuing...
        )

To start the export, just open the url in your browser::
    
    http://localhost:8080/Plone/export_content


How to extend it
================

We try to cover the basic Plone types to export useful content out of Plone. We
cannot predict all usecases, but if you have custom requirements it's easy to
extend functionality. You have a few options:

 - You can pass additional wrappers to the ``get_item`` External Method. Of course you
   have to have these wrappers in your PYTHONPATH::

        http://localhost:8080/Plone/front-page/get_item?additional_wrappers=myproject.wrapper1.Wrapper;myproject.wrapper2.Wrapper

 - If you need something completely custom, you could override the ``get_item``
   and ``get_children`` External Methods.
