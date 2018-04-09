Developer install
=================

::

    pip install -e .

Run tests
=========

::

    py.test

Build & upload docs
===================

::

    make -C doc html
    git commit doc/_build/html
    git subtree push --prefix doc/_build/html origin gh-pages

Start a test webserver
======================

::

    FLASK_APP=meta.web FLASK_DEBUG=1 flask run

Create a database migration
===========================

If the database has been changed create a migration file, these will be
automatically applied to the database upon connecting

::

    alembic revision --autogenerate -m "Change message"

Create a test Postgresql database using vagrant
===

::

    vagrant up

    TEST_DATABASE=postgresql://test:test@localhost/test py.test

Use the database for CLI commands with the flag::

    --database postgresql://test:test@localhost/metadb
