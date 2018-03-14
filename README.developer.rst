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
