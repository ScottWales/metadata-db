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
import six
import time

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


# def crawl_recursive(session, basedir, collection=None, parent=None):
#     """
#     Recursively crawl a directory, creating :py:class:`~metadb.model.Path` s in
#     the database
# 
#     :param session: SQLAlchemy session
#     :param basedir: Base directory to crawl
#     :param collection: Collection to put the found paths in
#     """
#     basedir = abspath(basedir)
# 
#     if parent is None:
#         parent = find_path(session, basedir)
#         assert parent is not None
# 
#     for entry in scandir(basedir):
#         p = find_or_create(session, Path, basename=entry.name, parent=parent)
#         p.collections.add(collection)
# 
#         try:
#             p.update_stat(entry.stat())
#             if entry.is_dir() and not entry.is_symlink():
#                 print(entry.path)
#                 crawl_recursive(session, entry.path, collection, parent)
#         except PermissionError:
#             # Not readable
#             pass
#         except FileNotFoundError:
#             # Broken symlink
#             pass
#         except OSError:
#             # Other error (e.g. recursive symlink)
#             pass

def crawl_recursive(session, basedir, collection, parent=None):
    basedir = os.path.abspath(str(basedir))

    if parent is None:
        parent = find_path(session, basedir)
        assert parent is not None

    crawl_recursive_impl(session, basedir, collection, parent, time.time())

def crawl_recursive_impl(session, basedir, collection, parent, last_seen):

    children = {c.basename: c for c in parent.children}
    new_children = {}

    for entry in scandir(basedir):
        if entry.name in children:
            p = children[entry.name]
            p.update_stat(entry.stat(), last_seen)
        else:
            try:
                new_children[entry.name] = entry.stat()
            except PermissionError:
                # Not readable
                pass
            except FileNotFoundError:
                # Broken symlink
                pass
            except OSError:
                # Other error (e.g. recursive symlink)
                pass

    new_paths = []
    for name, stat in six.iteritems(new_children):
        p = Path(basename=name, parent=parent)
        p.update_stat(stat, last_seen)
        new_paths.append(p)

    session.add_all(new_paths)

    for entry in scandir(basedir):
        if entry.is_dir(follow_symlinks=False):
            new_parent = session.query(Path).filter(Path.parent == parent, Path.basename == entry.name).one()
            crawl_recursive_impl(session, entry.path, collection, new_parent, last_seen)

    print(basedir)

