
import os
import logging
import ConfigParser

from App.config import getConfiguration

from collective.plone2x_jsonify.base import BaseWrapper
from collective.plone2x_jsonify.base import DCWrapper
from collective.plone2x_jsonify.base import ZopeObjectWrapper
from collective.plone2x_jsonify.at import ArchetypesWrapper
from collective.plone2x_jsonify.cmf import DocumentWrapper
from collective.plone2x_jsonify.cmf import LinkWrapper
from collective.plone2x_jsonify.cmf import NewsItemWrapper
from collective.plone2x_jsonify.cmf import ListCriteriaWrapper
from collective.plone2x_jsonify.cmf import StringCriteriaWrapper
from collective.plone2x_jsonify.cmf import DateCriteriaWrapper
from collective.plone2x_jsonify.cmf import FileWrapper
from collective.plone2x_jsonify.cmf import ImageWrapper
from collective.plone2x_jsonify.cmf import EventWrapper

logger = logging.getLogger('collective.plone2x_jsonify')
config = ConfigParser.SafeConfigParser()
config.optionxform = str

try:
    config.readfp(open(os.path.join(
            getConfiguration().instancehome,
            'plone2x_jsonify.ini')))
except:
    config.readfp(open(os.path.join(
            os.path.dirname(__file__),
            'config.ini')))

def get_mapping(section):
    mapping = {}
    if config.has_section(section):
        for x in config.items(section):
            try:
                mapping[x[0]] = eval(x[1].strip())
                logger.debug("map %s to %s" % (x[0], x[1]) )
            except:
                logger.info("cant add class for mapping %s" %  x[0])
                pass
    return mapping

PORTALTYPE_WRAPPERS = get_mapping('PORTALTYPE_WRAPPERS')
CLASSNAME_WRAPPERS = get_mapping('CLASSNAME_WRAPPERS')
