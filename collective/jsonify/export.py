"""Add as external method. See install.rst in the documentation.
"""
from collective.jsonify.methods import _clean_dict
from collective.jsonify.wrapper import Wrapper
from datetime import datetime
import logging
import os
# import pprint
import shutil
# import sys
# import traceback
try:
    import simplejson as json
except ImportError:
    import json

logger = logging.getLogger('collective.jsonify export')


COUNTER = 1
BATCH_START = None
BATCH_SIZE = None
BATCH_PREVIOUS_PATH = None
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
    '/Plone/kupu_library_tool',
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


def export_content(self,
                   basedir=HOMEDIR,
                   extra_skip_id=[],
                   extra_skip_classname=[],
                   extra_skip_paths=[],
                   batch_start=None,
                   batch_size=None,
                   batch_previous_path=None):
    global COUNTER
    global TMPDIR
    global ID_TO_SKIP
    global CLASSNAME_TO_SKIP
    global PATHS_TO_SKIP
    global BATCH_START
    global BATCH_SIZE
    global BATCH_PREVIOUS_PATH

    COUNTER = 1
    BATCH_START = batch_start
    BATCH_SIZE = batch_size
    BATCH_PREVIOUS_PATH = batch_previous_path

    TODAY = datetime.today()
    TMPDIR = basedir + '/content_' + \
        self.getId() + '_' + TODAY.strftime('%Y-%m-%d-%H-%M-%S')

    ID_TO_SKIP += list(extra_skip_id)
    id_to_skip = self.REQUEST.get('id_to_skip', None)
    if id_to_skip is not None:
        ID_TO_SKIP += id_to_skip.split(',')

    CLASSNAME_TO_SKIP += list(extra_skip_classname)
    classname_to_skip = self.REQUEST.get('classname_to_skip', None)
    if classname_to_skip is not None:
        CLASSNAME_TO_SKIP += classname_to_skip(',')

    PATHS_TO_SKIP += list(extra_skip_paths)
    paths_to_skip = self.REQUEST.get('paths_to_skip', None)
    if paths_to_skip is not None:
        PATHS_TO_SKIP += paths_to_skip(',')

    if os.path.isdir(TMPDIR):
        shutil.rmtree(TMPDIR)
    else:
        os.mkdir(TMPDIR)

    write(walk(self))

    count_sub = 0
    if BATCH_START is not None:
        count_sub = BATCH_START
    msg = 'SUCCESS :: exported %s items from %s' % (
        COUNTER - count_sub,
        self.absolute_url()
    )
    if BATCH_START is not None:
        msg = '%s\nstarting from count: %s' % (msg, BATCH_START)
    if BATCH_SIZE is not None:
        msg = '%s\nexportung until count: %s' % (
            msg, BATCH_START + BATCH_SIZE - 1)
    logger.info(msg)
    return msg


def walk(folder):
    for item_id in folder.objectIds():
        item = folder[item_id]

        path = '/'.join(item.getPhysicalPath())
        if filter(lambda x: x in path, PATHS_TO_SKIP)\
                or item.__class__.__name__ in CLASSNAME_TO_SKIP\
                or item.getId() in ID_TO_SKIP:
            continue
        if item.__class__.__name__ in CLASSNAME_TO_SKIP_LOUD:
            logger.warn('>> SKIPPING :: [%s] %s' % (
                item.__class__.__name__,
                item.absolute_url()
            ))
            continue
        yield item
        if getattr(item, 'objectIds', None) and item.objectIds():
            for subitem in walk(item):
                yield subitem


def write(items):
    global COUNTER
    """
    Batching example table:
        b_start = 0, b_size = 1000, counter = 1000: writes
        b_start = 1000, b_size = 1000, counter = 1000: breaks
        b_start = 1000, b_size = 1000, counter = 1001: writes
    """

    for item in items:
        if BATCH_START is not None\
                and BATCH_SIZE is not None\
                and COUNTER >= BATCH_START + BATCH_SIZE:
            # BATCH UNTIL
            break

        ppath = '/'.join(item.getPhysicalPath())

        if BATCH_PREVIOUS_PATH is not None\
                and BATCH_START is not None:
            # MEMORY SAVING BATCHING
            if BATCH_PREVIOUS_PATH == ppath:
                # BATCH_PREVIOUS_PATH is the path of the last item, which was
                # successfully exported in a previous batch. BATCH_START is the
                # counting state from where the new batch begins. We set
                # COUNTER to this state here:
                COUNTER = BATCH_START
                # Reset BATCH_PREVIOUS_PATH, so we don't visit this conditional
                # branch again.
                global BATCH_PREVIOUS_PATH
                BATCH_PREVIOUS_PATH = None
            continue  # Always continue in this conditional branch.

        json_structure = None

        try:
            context_dict = Wrapper(item)
        except Exception, e:
            # tb = pprint.pformat(traceback.format_tb(sys.exc_info()[2]))
            # msg = 'ERROR: exception wrapping object: %s\n%s' % (str(e), tb)
            logger.warn('exception wrapping object %s. Error: %s' % (ppath, e))
            continue

        passed = False
        while not passed:
            try:
                # see, if we can serialize to json
                json_structure = json.dumps(context_dict)  # noqa
                passed = True
            except Exception, error:
                if "serializable" in str(error):
                    key, context_dict = _clean_dict(context_dict, error)
                    logger.warn(
                        'Not serializable member %s of %s ignored. (%s)' % (
                            key,
                            repr(item),
                            ppath
                        )
                    )
                    passed = False
                else:
                    logger.warn(
                        'ERROR: Unknown error serializing object %s: %s' % (
                            ppath,
                            error
                        )
                    )
                    continue

        if passed:
            if BATCH_START is not None and COUNTER < BATCH_START:
                # BATCH FROM
                COUNTER += 1
                continue
            write_to_jsonfile(context_dict)
            logger.info('exported %s to %s' % (
                ppath,
                os.path.join(
                    TMPDIR,
                    str(COUNTER / 1000),
                    str(COUNTER) + '.json'
                )
            ))
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
