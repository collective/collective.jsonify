from setuptools import setup, find_packages

version = '0.1'

setup(
    name='collective.plone2x_jsonify',
    version=version,
    description="provide json representation for content in Plone 2.0, 2.1 and 2.5",
    long_description=open("README.rst").read(),
    classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
    keywords='',
    author='',
    author_email='',
    url='https://github.com/collective/collective.plone2x_jsonify',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['collective'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        ],
    )
