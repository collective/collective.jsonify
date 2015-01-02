Main reason for this package is to get an easy handle to Json export of Plone content 
objects for mobile APPs.

* GATHERING DATA:

We can get data as Anonymous user (but you should pass __ac_name and __ac_password in http call to get privileges)
by passin right ACTION parameter.
Actions for gatherin are:

    . QUERY -> use portal_catalog for data retrieving
    . LIST -> use portal_catalog but return COMPACT list of live objects
    . GET -> return the actual JSON of the objects

To get right answers you have to do right questions :)
Parameters are important. Here are some interesting examples:

- ACTION = QUERY : get MODIFIED (from date - to date) objects

http://www.myplonesite.com/custompath/deep/@@jsonify
?action=query
&portal_type=my_at_or_dexterity_type
&show_inactive=True
&modified:list:date=2013-01-01
&modified:list:date=2013-03-01
&modified_usage=range:min:max

MORE: if "available" parameter is added, it returns the NUMBER of objects the query returned, NULL if no returns
MORE: "send_bin" parameter is "False" by default. You can change this by passing "send_bin=True"
MORE: "absolute_urls" parameter is "True" by default. You can change this by passing "absolute_urls=False"
IMPORTANT: "path" parameter is not needed: is always considered in the query, from URL path


- ACTION = LIST : COMPACT LIST OF LIVE OBJECTS

Why should I get it? Because by comparing it with the objects list in your mobile APP, you can have an evidence 
of DELETED objects. 
What is returned: [{"uid":value,"path":value}]
What you cannot get: when an object has been deleted.



* BINARY FIELDS:

- binary fields names starts with "_datafield_" and are exported as dictionary, so you 
can download data separatly. 

Example: An Image field called "photo" from a custom Archetype content is exported as:

"_datafield_photo": "{\"filename\": \"alpino-pizzeria.jpg\", \"data\": \" \", \"content_type\": \"image/jpeg\", \"size\": 55536, "md5": "fa2b0abcf540d2dde71d68071140a803"}"



* TO DO:

- Add parameter for excluding fields in the export
- Implement EDITING DATA actions ? 


CODE FROM:
Using wrapper.py from original collective.jsonify. Thanks to Rok Garbas

QUESTIONS / CONTRIBUTIONS:
.. _Giorgio Pieretti: giorgio.pieretti@openprojects.it

:Warning: This product is in Beta.
:Author: Giorgio Pieretti
:Source: http://github.com/collective/collective.jsonify

