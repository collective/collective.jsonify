"""Add as external method. See install.rst in the documentation.
"""
from collective.jsonify.methods import _clean_dict
from collective.jsonify.wrapper import Wrapper
from datetime import datetime
import os
import pprint
import shutil
import simplejson
import sys
import traceback
try:
    import simplejson as json
except ImportError:
    import json


COUNTER = 1
HOMEDIR = '/tmp'
TMPDIR = HOMEDIR
CLASSNAME_TO_SKIP_LOUD = [
    'BrowserIdManager',
    'Connection',
    'ControllerPageTemplate',
    'ControllerPythonScript',
    'ControllerValidator',
    'ExternalMethod',
    'I18NLayer',
    'PythonScript',
    'SQL',
    'SiteRoot',
    'ZetadbApplication',
    'ZetadbMysqlda',
    'ZetadbScript',
    'ZetadbScriptSelectMaster',
    'ZetadbSqlInsert',
    'ZetadbSqlSelect',
    'ZetadbZptInsert',
    'ZetadbZptView',
]
CLASSNAME_TO_SKIP = [
    'AcceleratedHTTPCacheManager',
    'ActionIconsTool',
    'ActionsTool',
    'ArchetypeTool',
    'CachingPolicyManager',
    'CalendarTool',
    'CatalogTool',
    'ContentPanelsTool',
    'ContentTypeRegistry',
    'CookieCrumbler',
    'DiscussionTool',
    'FactoryTool',
    'FormController',
    'FormTool',
    'GroupDataTool',
    'GroupUserFolder',
    'GroupsTool',
    'InterfaceTool',
    'LanguageTool',
    'MailHost',
    'MemberDataTool',
    'MembershipTool',
    'MetadataTool',
    'MigrationTool',
    'MimeTypesRegistry',
    'NavigationTool',
    'PloneArticleTool',
    'PloneControlPanel',
    'PloneTool',
    'PropertiesTool',
    'QuickInstallerTool',
    'RAMCacheManager',
    'ReferenceCatalog',
    'RegistrationTool',
    'SinTool',
    'SiteErrorLog',
    'SkinsTool',
    'SyndicationInformation',
    'SyndicationTool',
    'TransformTool',
    'TypesTool',
    'UIDCatalog',
    'URLTool',
    'UndoTool',
    'WorkflowTool',
]

ID_TO_SKIP = ['Members', ]

PATHS_TO_SKIP = [
    '/HTTPCache',
    '/MailHost',
    '/RAMCache',
    '/access_rule',
    '/acl_users',
    '/archetype_tool',
    '/caching_policy_manager',
    '/challenge_hook',
    '/content_type_registry',
    '/error_log',
    '/marshaller_registry',
    '/mimetypes_registry',
    '/plone_utils',
    '/portal_actionicons',
    '/portal_actions',
    '/portal_article',
    '/portal_atct',
    '/portal_calendar',
    '/portal_catalog',
    '/portal_controlpanel',
    '/portal_css',
    '/portal_discussion',
    '/portal_enfold_utilities',
    '/portal_factory',
    '/portal_file_templates',
    '/portal_form_controller',
    '/portal_fss',
    '/portal_groupdata',
    '/portal_groups',
    '/portal_interface',
    '/portal_javascripts',
    '/portal_languages',
    '/portal_lock_manager',
    '/portal_memberdata',
    '/portal_membership',
    '/portal_metadata',
    '/portal_migration',
    '/portal_password_reset',
    '/portal_placeful_workflow',
    '/portal_properties',
    '/portal_quickinstaller',
    '/portal_registration',
    '/portal_setup',
    '/portal_skins',
    '/portal_squid',
    '/portal_syndication',
    '/portal_transforms',
    '/portal_types',
    '/portal_uidannotation',
    '/portal_uidgenerator',
    '/portal_uidhandler',
    '/portal_undo',
    '/portal_url',
    '/portal_vocabularies',
    '/portal_workflow',
    '/property_set_registry',
    '/reference_catalog',
    '/translation_service',
    '/uid_catalog',
    '/workflow_catalog',
]


def export_content(self):
    global COUNTER
    global TMPDIR
    global ID_TO_SKIP

    COUNTER = 1
    TODAY = datetime.today()
    TMPDIR = HOMEDIR + '/content_' + \
        self.getId() + '_' + TODAY.strftime('%Y-%m-%d-%H-%M-%S')

    id_to_skip = self.REQUEST.get('id_to_skip', None)
    if id_to_skip is not None:
        ID_TO_SKIP += id_to_skip.split(',')

    if os.path.isdir(TMPDIR):
        shutil.rmtree(TMPDIR)
    else:
        os.mkdir(TMPDIR)

    write(walk(self))

    # TODO: we should return something more useful
    return 'SUCCESS :: ' + self.absolute_url() + '\n'


def walk(folder):
    for item_id in folder.objectIds():
        item = folder[item_id]

        path = '/'.join(item.getPhysicalPath())
        if filter(lambda x: x in path, PATHS_TO_SKIP)\
                or item.__class__.__name__ in CLASSNAME_TO_SKIP\
                or item.getId() in ID_TO_SKIP:
            continue
        if item.__class__.__name__ in CLASSNAME_TO_SKIP_LOUD:
            print '>> SKIPPING :: [%s] %s' % (
                item.__class__.__name__,
                item.absolute_url()
            )
            continue
        yield item
        if getattr(item, 'objectIds', None) and item.objectIds():
            for subitem in walk(item):
                yield subitem


def write(items):
    global COUNTER

    for item in items:

        json_structure = None

        try:
            context_dict = Wrapper(item)
        except Exception, e:
            tb = pprint.pformat(traceback.format_tb(sys.exc_info()[2]))
            return 'ERROR: exception wrapping object: %s\n%s' % (str(e), tb)

        passed = False
        while not passed:
            try:
                # see, if we can serialize to json
                json_structure = json.dumps(context_dict)  # noqa
                passed = True
            except Exception, error:
                if "serializable" in str(error):
                    key, context_dict = _clean_dict(context_dict, error)
                    pprint.pprint(
                        'Not serializable member %s of %s ignored' % (
                            key, repr(item)
                        )
                    )
                    passed = False
                else:
                    return (
                        'ERROR: Unknown error serializing object: %s' % error)

        if passed:
            write_to_jsonfile(context_dict)
            COUNTER += 1


def write_to_jsonfile(item):
    global COUNTER

    # 1000 files per folder, so we dont reach some fs limit
    SUB_TMPDIR = os.path.join(TMPDIR, str(COUNTER / 1000))
    if not os.path.isdir(SUB_TMPDIR):
        os.mkdir(SUB_TMPDIR)

    f = open(os.path.join(SUB_TMPDIR, str(COUNTER) + '.json'), 'wb')
    json.dump(item, f, indent=4)
    f.close()
