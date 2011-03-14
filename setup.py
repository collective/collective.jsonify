from setuptools import setup, find_packages

version = '0.1'

setup(
    name='collective.jsonify',
    version=version,
    description="provide json representation for content in Plone 2.0, 2.1, 2.5 and above",
    long_description=open("README.rst").read(),
    classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
    keywords='',
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
