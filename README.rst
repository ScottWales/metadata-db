metadata-db
===========

.. image:: https://travis-ci.org/ScottWales/metadata-db.svg?branch=master
    :target: https://travis-ci.org/ScottWales/metadata-db
    :alt: Test Status
.. image:: https://api.codeclimate.com/v1/badges/d5cc1000b0b6bc951ebb/test_coverage
   :target: https://codeclimate.com/github/ScottWales/metadata-db/test_coverage
   :alt: Test Coverage
.. image:: https://api.codeclimate.com/v1/badges/d5cc1000b0b6bc951ebb/maintainability
   :target: https://codeclimate.com/github/ScottWales/metadata-db/maintainability
   :alt: Maintainability


Read files into the database::

    metadb import /path/to/files


Get a list of files matching given constraints::

    metadb list --file-attribute project_id CMIP5 \
                --file-attribute experiment historical \
                --variable-attribute standard_name precipitation_flux
