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
        if item.__class__.__name__ in CLASSNAME_TO_SKIP or \
           item.getId() in ID_TO_SKIP:
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

        JSON = None

        try:
            context_dict = Wrapper(item)
        except Exception, e:
            tb = pprint.pformat(traceback.format_tb(sys.exc_info()[2]))
            return 'ERROR: exception wrapping object: %s\n%s' % (str(e), tb)

        passed = False
        while not passed:
            try:
                JSON = json.dumps(context_dict)
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
        return JSON

        write_to_jsonfile(JSON)
        COUNTER += 1


def write_to_jsonfile(item):
    global COUNTER

    # 1000 files per folder, so we dont reach some fs limit
    SUB_TMPDIR = os.path.join(TMPDIR, str(COUNTER / 1000))
    if not os.path.isdir(SUB_TMPDIR):
        os.mkdir(SUB_TMPDIR)

    f = open(os.path.join(SUB_TMPDIR, str(COUNTER) + '.json'), 'wb')
    simplejson.dump(item, f, indent=4)
    f.close()
