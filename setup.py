#!/usr/bin/env python
import sys
if sys.version_info < (2, 3):
    from distutils.core import setup

    def find_packages(exclude=None):
        return ['collective', 'collective.jsonify']
else:
    from setuptools import setup, find_packages

version = '1.2'

requirements = [
    'setuptools',
]

# since Python 2.6 simplejson is not needed anymore
try:
    import json
except ImportError:
    requirements.append('simplejson')

setup(
    name='collective.jsonify',
    version=version,
    description="JSON representation for content in Plone from 2.0 and above",
    long_description="%s\n%s" % (
        open("README.rst").read(),
        open("CHANGES.rst").read(),
    ),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.4",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
    ],
    keywords='Plone content export json transmogrify',
    author='Rok Garbas',
    author_email='rok@garbas.si',
    url='https://github.com/collective/collective.jsonify',
    license='GPL',
    packages=find_packages(),
    namespace_packages=['collective'],
    include_package_data=True,
    zip_safe=False,
    install_requires=requirements,
)
