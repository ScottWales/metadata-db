metadata-db
===========

.. image:: https://img.shields.io/circleci/project/github/ScottWales/metadata-db.svg
   :target: https://circleci.com/gh/ScottWales/metadata-db
   :alt: Circle CI status
.. image:: https://api.codeclimate.com/v1/badges/d5cc1000b0b6bc951ebb/test_coverage
   :target: https://codeclimate.com/github/ScottWales/metadata-db/test_coverage
   :alt: Test Coverage
.. image:: https://img.shields.io/codeclimate/maintainability/ScottWales/metadata-db.svg
   :target: https://codeclimate.com/github/ScottWales/metadata-db/maintainability
   :alt: Maintainability

Create a new collection::

    metadb collection --name my-data

Read files into the database::

    metadb import /path/to/files
    metadb import --collection my-data /path/to/files


Get a list of files matching given constraints::

    metadb list --file-attribute project_id CMIP5 \
                --file-attribute experiment historical \
                --variable-attribute standard_name precipitation_flux
