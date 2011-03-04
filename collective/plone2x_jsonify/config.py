
import os
import logging
import ConfigParser

from App.config import getConfiguration


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
