from setuptools import setup, find_packages

version = '0.1.2.dev0'

long_description = (
    open('README.rst').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.rst').read()
    + '\n' +
    open('CHANGES.rst').read()
    + '\n')

setup(
    name='gites.pivot.core',
    version=version,
    description="Pivot import tools and scripts",
    long_description=long_description,
    # Get more strings from
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Framework :: Plone",
        "Framework :: Plone :: 4.2",
    ],
    keywords='Plone',
    author='Affinitic',
    author_email='support@lists.affinitic.be',
    url='https://github.com/gitesdewallonie/',
    license='GPL',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['gites', 'gites.pivot'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'Plone',
        'gites.core',
        'gites.db',
        'gites.pivot.db',
        'plone.api',
        'plone.z3ctable',
    ],
    extras_require={
        'test': [
            'affinitic.testing',
            'gites.pivot.db [test]',
            'plone.app.testing',
        ],
        'docs': [
            'docutils',
        ],
    },
    entry_points={
        'console_scripts': [
            'import_pivot_changes = gites.pivot.core.scripts.changes:main',
        ]}
)
