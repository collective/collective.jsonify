# -*- coding: utf-8 -*-
import pkg_resources
import datetime
import sphinx_rtd_theme

html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.coverage',
    'sphinx.ext.viewcode'
]
source_suffix = '.rst'
master_doc = 'index'

project = u'collective.jsonify'
this_year = datetime.date.today().year
copyright = u'{}, Rok Garbas, et. al.'.format(this_year)
version = pkg_resources.get_distribution('collective.jsonify').version
release = version

exclude_patterns = ['_build', 'lib', 'bin', 'include', 'local']
pygments_style = 'sphinx'
