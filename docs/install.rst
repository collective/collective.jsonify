How to install it
=================

put ``collective.jsonify`` and ``simplejson`` in your PYTHON_PATH. Now how you
do this it does not really matter. You could:

1. play with PYTHON_PATH manually
2. use ``easy_install collective.jsonify`` or ``pip collective.jsonify`` which
   will also pull ``simplejson``
3. using buildout. add it under eggs option for instance you want to do
   migration from.


Next you create script in Extensions folder with following content::

    from collective.jsonify import get_item
    from collective.jsonify import get_children

Then run zope instance got to Zope root and create 2 External methods:

 - get_item ()
 - get_children ()


Its true External methods are not the nicest way to work with and this makes
setup a little long. But nice thing with External Scripts is that they work in
Plone 1.0 as well as in Plone 4.0, so you could potentially use
``collective.jsonify`` to migrate from Plone 4.0.


How to use it
=============

``collective.jsonify`` was developed with pupose to be used by
``collective.jsonmigrator``. There you can find transmogrifier blueprint that
connects to Plone site, crawls it and extracts content.

To see what ``collective.jsonmigrator`` is actually seeing you can issue "json
views" on contet you want to explore::

    http://localhost:8080/Plone/front-page/get_item
    http://localhost:8080/Plone/front-page/get_children

First gets all content out of ``front-page``, second lists all content
contained inside this object and returns their ids.


How to extend it
================

We try to cover basic Plone types and export usefull content out of Plone. But
we can not predict all usecases so please see testing section what is covered
in in export scripts. We will be more then happy to add some export functionality.

But in case you have some strange custom requirements its easy to extend
functionality. You have few options:

 - You can pass additional wrappers to get_item External Method. Ofcourse you
   have to provide this wrappers in PYTHON_PATH::

        http://localhost:8080/Plone/front-page/get_item?additional_wrappers=myproject.wrapper1.Wrapper;myproject.wrapper2.Wrapper

 - If you need something completely custom, you could also override get_item
   and get_children external methods.
