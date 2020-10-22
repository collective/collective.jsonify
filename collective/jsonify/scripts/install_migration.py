# Installs collective.jsonify as external method into the Zope root.
# Needed for Plone 4.3 -> Plone 5.2 migration through JSON export.

import transaction

manage_addProduct = app.manage_addProduct

if 'export_content' in app.objectIds():
    app.manage_delObjects(['export_content'])

em = manage_addProduct['ExternalMethod']
manage_addExternalMethod = em.manage_addExternalMethod
manage_addExternalMethod(
        'export_content',
        'export_content',
        'collective.jsonify.json_methods',
        'export_content')
transaction.commit()