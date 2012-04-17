from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from plone.portlets.constants import USER_CATEGORY
from plone.portlets.interfaces import IPortletManager
from zope.component import getUtility


EXCLUDED_ATTRIBUTES = ['__name__', '__parent__']


class DashboardWrapper(dict):
    """Gets the all dasbhoard configurations in a format
    that can be used by the blueprints in collective.jsonmigrator"""

    def __init__(self, context, userid):
        self.context = context
        self._context = aq_base(context)
        self.portal = getToolByName(
            self.context, 'portal_url').getPortalObject()
        self.pr = self.portal.portal_repository
        self.portal_path = '/'.join(self.portal.getPhysicalPath())
        self.portal_utils = getToolByName(self.context, 'plone_utils')
        self.charset = self.portal.portal_properties.site_properties.default_charset
        # newer seen it missing ... but users can change it
        if not self.charset:
            self.charset = 'utf-8'

        self.userid = userid

        for method in dir(self):
            if method.startswith('get_'):
                getattr(self, method)()

    def get_peronal_dashboard(self):

        dashboard_names = ['plone.dashboard1',
                            'plone.dashboard2',
                            'plone.dashboard3',
                            'plone.dashboard4']

        for name in dashboard_names:
            dashboard = getUtility(IPortletManager, name=name)
            AssignmentMapping = dashboard.get(
                USER_CATEGORY, {}).get(self.userid, {})

            self['userid'] = self.userid

            self['_manager_%s' % name] = []

            for assignment in AssignmentMapping.values():
                data = {'module': assignment.__module__,
                        'id': assignment.getId(), }
                for attr in assignment.__dict__.keys():
                    if attr not in EXCLUDED_ATTRIBUTES:
                        data[attr] = getattr(assignment, attr, '')

                self['_manager_%s' % name].append(data)
