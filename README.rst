metadata-db
===========

.. image:: https://img.shields.io/circleci/project/github/ScottWales/metadata-db/master.svg
   :target: https://circleci.com/gh/ScottWales/metadata-db
   :alt: Circle CI status
.. image:: https://img.shields.io/codeclimate/coverage/ScottWales/metadata-db.svg
   :target: https://codeclimate.com/github/ScottWales/metadata-db/test_coverage
   :alt: Test Coverage
.. image:: https://img.shields.io/codeclimate/maintainability/ScottWales/metadata-db.svg
   :target: https://codeclimate.com/github/ScottWales/metadata-db/maintainability
   :alt: Maintainability

Create a new collection::

    metadb create --collection my-data /base/path

Update all files under the base path for a single collection::

    metadb crawl --collection my-data

Or for all of them::

    metadb crawl

Add or update individual files::

    metadb import --collection my-data path/to/file

Get a list of files matching given constraints::

    metadb list --file-attribute project_id CMIP5 \
                --file-attribute experiment historical \
                --variable-attribute standard_name precipitation_flux

Report the size of each collection::

    metadb report
