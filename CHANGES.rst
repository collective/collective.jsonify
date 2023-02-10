Changelog
=========

1.6 (2023-02-10)
----------------

- Fix "AttributeError: get" that occurred with collective.jsonify 1.5 on Plone 2.1,
  by using objectValues() to list items contained in a folder.
  [rpijlman]

- Add additional_wrappers to hook into export as promised by the documentation.
  [pbauer]

- Do not export None in a DateTimeField as the string "None".
  [pbauer]


1.5 (2020-08-21)
----------------

- Fixing Out of Memory by swapping base64 implementation.
  [gogobd]

- Fix acquisition when object in folder has attribute name.
  [maartenkling]

- Fallback for TypeError when _get_at_field_value is broken computedfield.
  [maartenkling]

- Add runhook support.
  [gotcha]


1.4 (2018-09-20)
----------------

- Try Subject and Contributors when subject and contributors give nothing.
  [maurits]

- Check if value exists on file like fields
  [agitator]

- Export creation_date and modification_date for all objects, not only _is_cmf_only_obj.
  For dexterity these values are not present in a schemata, so they are not included as part
  of the normal schemata based dexterity export.
  [sunew]

- Use self.decode method to get stringified field value when wrapping content
  for export.
  [instification]


1.3 (2017-12-21)
----------------

- Export plone.app.redirector redirects, if available.
  Comply with default expectations of redirector section in plone.app.transmogrifier.
  [hvelarde]

- Do not export FormGen and Redirection tools.
  [hvelarde]

- Show translations from LinguaPlone if canonical is available.
  [agitator]

- Fixed value for unknown fields.  The value was never calculated
  fresh for these fields, so you got the value of the previous field.
  Or you probably got a NameError if this was the first field.
  [maurits]

- Fix manifest
- Added `CHANGES.rst merge=union` to `.gitattributes`
  [ale-rt]

- Added the history to JSON export.
  [rristow]


1.2 (2016-05-24)
----------------

- Do not require simplejson if we already have the native json module
  [ale-rt]

- When doing an export with ``export_content`` and having constraints to skip
  items, still allow to walk into subitems of the skipped ones - except for
  skipped paths, where the whole path is skipped.
  [thet]


1.1 (2015-10-22)
----------------

- set json repsonse headers
  [jensens]


1.0 (2015-05-16)
----------------

- Let the wrapper test correctly for ``zope.interface`` and ``Interface``
  interfaces.
  [thet]

- In the wrapper class, call the value in decode, if it's a callable.
  [thet]

- When serializing datetime, date, time or DateTime properties, just use the
  unicode representation which can be parsed.
  [thet]

- When serializing values, if there is no special handler for a field type,
  just try to unicode the value.
  [thet]

- Fix export of defaultPage and layout. Before, always the defaultPage was set
  now layout is always set and defaultPage only, if there is one defined.
  [thet]

- Handle plone.formwidget.geolocation Dexterity field types.
  [thet]

- Check, if wrapper methods for Zope/CMF objects are Zope/CMF only objects by
  testing for Archetypes and Dexterity first.
  [thet]

- Add ``BlobField`` for ``get_archetypes_fields``.
  [thet]

- Don't try to convert ints to unicode in get_properties().
  [djowett]

- Zope 2.6 support for collective.jsonify.
  [djowett]

- Fix setup.py to work with Python 2.2.
  [djowett]

- Add error type to tracebacks.
  [djowett]

- Fix read of NamedBlobImage, NamedFile and NamedBlobFile in dexterity objects.
  [djowett]

- Fix read of field for unicode transcoding in dexterity objects.
  [djowett]

- Make ``archetypes.schemaextender`` support more generic and handle probably
  most use cases.
  [thet]

- Add ``_directly_provided`` export field for the object's directly provided
  interfaces.
  [thet]

- Add json_methods module to own Extension folder, which makes it automatically
  available and unnecessary to add it to the instance's Extension folder.
  [thet]

- Don't skip ``ComputedField`` fields, but just export their computed value.
  Better skip them in your transmogrifier import pipeline.
  [thet]

- Allow a ``skip_callback`` function to be passed to the ``export_content``
  function. It evaluates to ``True``, if the current visited item should be
  excluded from exporting.
  [thet]

- Export a content's references as list of UID values.
  [thet]

- Declare the ``content_type`` of a field's value only for ``TextField`` and
  ``StringField``.
  [thet]

- Add example buildouts for Plone 2.1, 2.5, 3 and 4.
  [thet]

- Declare ``base64`` encoding for _datafield_FIELDNAME structures. This is used
  to correctly decode in transmogrify.dexterity.
  [thet]

- Add export module from ``collective.blueprint.jsonmigrator`` and modify to
  use collective.jsonify wrapper. Use it in Plone 2.1 by adding it as external
  method.
  [thet]

- PEP 8.
  [thet]

- Fixing local roles export.
  [realefab]

- Make ATExtensionFields serializable.
  [jsbueno]

- Fixes exporting of Image types that use ATBlob.
  [jsbueno]


0.2 (2014-08-18)
----------------

- Support p.a.collection QueryField.
  [jone]

- Dexterity support.
  [djowett]

- Add Blob fields support. Use specific methods to retrieve
  filename, content type and size.
  [gborelli]

- Add _get_at_field_value to wrappe.Wrapper in order to use accessor method
  for Archetypes fields.
  [gborelli]

- @@jsonify view added. See README_JSONIFY_VIEW.rst for more
  [pieretti]


0.1 (2011-03-14)
----------------

- documentation added
  [garbas]

- collection of external methods from ``collective.blueprint.jsonmigrator``
  and ``collective.sync_migrator``.
  [garbas]

- initial release
  [garbas]
