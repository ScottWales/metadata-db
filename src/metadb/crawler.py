#!/usr/bin/env python
# Copyright 2018 Scott Wales
# author: Scott Wales <scott.wales@unimelb.edu.au>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import print_function
from .model import Path
from .query import find_or_create, find_path
import os

"""
Filesystem crawler
"""

try:
    from os import scandir
except ImportError:
    from scandir import scandir

# FileNotFoundError not available in Python 2
try:
    FileNotFoundError
except NameError:
    PermissionError = IOError
    FileNotFoundError = OSError


def abspath(path):
    try:
        return os.path.abspath(path)
    except AttributeError:
        return os.path.abspath(str(path))


def crawl_recursive(session, basedir, collection=None, parent=None):
    """
    Recursively crawl a directory, creating :py:class:`~metadb.model.Path` s in
    the database

    :param session: SQLAlchemy session
    :param basedir: Base directory to crawl
    :param collection: Collection to put the found paths in
    """
    basedir = abspath(basedir)

    if parent is None:
        parent = find_path(session, basedir)
        assert parent is not None

    for entry in scandir(basedir):
        print(entry.path)
        p = find_or_create(session, Path, basename=entry.name, parent=parent)
        p.collections.add(collection)

        try:
            p.update_stat(entry.stat())
            if entry.is_dir() and not entry.is_symlink():
                crawl_recursive(session, entry.path, collection, parent)
        except PermissionError:
            # Not readable
            pass
        except FileNotFoundError:
            # Broken symlink
            pass
