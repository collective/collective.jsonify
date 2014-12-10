Changelog
=========

0.3 (unreleased)
----------------

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