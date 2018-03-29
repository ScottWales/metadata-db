#!/usr/bin/env python
from __future__ import print_function
from setuptools import setup, find_packages
import versioneer

setup(
    name='metadb',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),

    package_data={
        'metadb': [
            'templates/*.html',
            'migrations/*',
            'migrations/versions/*'],
    },

    install_requires=[
        'sqlalchemy',
        'psycopg2',
        'netcdf4',
        'flask',
        'pandas',
        'mock;python_version<"3"',
        'scandir;python_version<"3"',
        'alembic',
    ],
    extras_require={
        'test': [
            'pytest',
            'pytest-cov',
        ],
    },
    entry_points={
        'console_scripts': [
            'metadb = metadb.cli:cli',
        ]}
)
