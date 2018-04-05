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
from .model import Path, path_to_collection
from .query import find_or_create, find_path
import os
import six
import time
from sqlalchemy.sql.expression import select, literal
from sqlalchemy.orm import aliased

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


def crawl_recursive(session, basedir, collection, parent=None):
    basedir = os.path.abspath(str(basedir))

    if parent is None:
        parent = find_path(session, basedir)
        assert parent is not None

    crawl_recursive_impl(
        session,
        basedir.encode('utf8').decode('utf8', 'backslashreplace'),
        collection,
        parent,
        time.time())

    session.commit()

    # Insert the collection
    children = (
        select([
            literal(collection.id).label('coll_id'),
            literal(parent.id).label('path_id')
        ])
        .cte(name='children', recursive=True))

    cte = children.alias(name='cte')

    children = (
        children.union_all(
            select([
                literal(collection.id).label('coll_id'),
                Path.id.label('path_id')
            ])
            .where(Path.parent_id == cte.c.path_id))
        .alias(name='foo'))

    if session.bind.dialect.name == 'postgresql':
        from sqlalchemy.dialects.postgresql import Insert
        insert = Insert(path_to_collection).on_conflict_do_nothing()
    else:
        from sqlalchemy.sql import Insert
        insert = Insert(path_to_collection).prefix_with('OR IGNORE', dialect='sqlite')


    session.execute(insert.from_select(
                        ['coll_id', 'path_id'],
                        select([children.c.coll_id, children.c.path_id]))
                    )


def crawl_recursive_impl(session, basedir, collection, parent, last_seen):

    children = {c.basename: c for c in parent.children}
    new_paths = {}

    for entry in scandir(basedir):
        if entry.name in children:
            # Already exists, update
            p = children[entry.name]
            p.update_stat(entry.stat(), last_seen)
        else:
            # Record the stat if readable
            try:
                new_paths[entry.name] = entry.stat()
            except PermissionError:
                # Not readable
                pass
            except FileNotFoundError:
                # Broken symlink
                pass
            except OSError:
                # Other error (e.g. recursive symlink)
                pass

    # Convert the new stat()s to Path objects
    new_children = {}
    for name, stat in six.iteritems(new_paths):
        p = Path(basename=name, parent=parent)
        p.update_stat(stat, last_seen)
        new_children[name] = p

    # Add the new children
    session.add_all(six.itervalues(new_children))
    children.update(new_children)

    for entry in scandir(basedir):
        if entry.is_dir(follow_symlinks=False):
            new_parent = children[entry.name]
            crawl_recursive_impl(session, entry.path,
                                 collection, new_parent, last_seen)

    print(basedir)
