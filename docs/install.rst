How to install it
=================

Put ``collective.jsonify`` and ``simplejson`` in your PYTHONPATH. How you do
this does not really matter. You could:

1. Play with PYTHONPATH manually.
2. Use ``easy_install collective.jsonify`` or ``pip collective.jsonify`` which
   will also pull ``simplejson``.
3. Use buildout. Add it under the ``eggs`` option for the instance you want to
   migrate from.

Next, create a script in the Extensions folder with the following content::

    from collective.jsonify import get_item
    from collective.jsonify import get_children
    from collective.jsonify import get_catalog_results

Then run your Zope instance, go to the Zope root and create 3 External Methods:

 - get_item ()
 - get_children ()
 - get_catalog_results ()

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
