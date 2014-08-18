from setuptools import setup, find_packages

version = '0.2'

setup(
    name='collective.jsonify',
    version=version,
    description="provide json representation for content in Plone 2.0, 2.1, 2.5 and above",
    long_description=open("README.rst").read(),
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
    author='',
    author_email='',
    url='https://github.com/collective/collective.jsonify',
    license='GPL',
    packages=find_packages(),
    namespace_packages=['collective'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'simplejson',
        ],
    )
