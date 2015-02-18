"""Module with all imports used for the ExternalMethod's.
Then create external methods in ZMI for get_item, get_children,
get_catalog_results and export_content as described in the installation docs.
"""
from collective.jsonify import get_item  # noqa
from collective.jsonify import get_children  # noqa
from collective.jsonify import get_catalog_results  # noqa
from collective.jsonify.export import export_content as export_content_orig


def export_content(self):
    return export_content_orig(
        self,
        basedir='/tmp',  # absolute path to directory for the JSON export
        skip_callback=lambda item: False,  # optional callback. Returns True to skip an item.  # noqa
        extra_skip_classname=[],  # optional list of classnames to skip
        # batch_start=0,
        # batch_size=5000,
        # batch_previous_path='/absolute/path/to/last/exported/item'
    )
