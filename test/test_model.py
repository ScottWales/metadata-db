#!/usr/bin/env python
# Copyright 2018 ARC Centre of Excellence for Climate Systems Science
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

from metadb.model import *

import pytest


def test_db(session):
    q = session.query(Metadata)
    assert q.count() == 0


def test_collection(session):
    c = Collection(name='c')
    p = Path(collections=set((c,)))
    session.add(p)
    session.commit()

    q = (session.query(Path)
                .join(Path.collections)
                .filter(Collection.name == 'c')
                .one())
    assert q == p


def test_collection_repeat(session):
    c = Collection(name='c')
    p = Path(collections=set((c,)))
    session.add(p)

    session.query(Path).one()


def test_path(session):
    p = Path(basename='/foo/bar')
    session.add(p)

    m = Metadata(paths=[p])
    session.add(m)

    session.commit()

    assert p.path == '/foo/bar'

    path, meta = session.query(Path, Metadata).join(Path.meta).one()

    p1 = Path(basename='baz', parent=p)
    session.add(p1)
    session.commit()

    assert p1.path == '/foo/bar/baz'


# def test_path_property(database, session):
#     import metadb.model
#     import sqlparse
#     print(sqlparse.format(str(metadb.model._path_path_property(Path)),reindent=True))
#     assert False
#    a = Path(basename='a')
#    session.add(a)
#    session.commit()
#
#    q = metadb.model._path_path_property(a)
#    r = database.execute(q).fetchall()
#    assert r == [('a',)]
#
#    b = Path(basename='b', parent=a)
#    session.add(b)
#    session.commit()
#
#    q = metadb.model._path_path_property(b)
#    r = database.execute(q).fetchall()
#    assert r == [('a/b',)]


def test_path_closure(session):
    if (session.bind.dialect.name == 'sqlite' and
            session.bind.dialect.server_version_info < (3, 8, 3)):
        pytest.skip("Sqlite too old")

    a = Path(basename='a')
    session.add(a)
    session.commit()

    assert a.parent is None
    assert a.path == 'a'

    b = Path(basename='b', parent=a)
    session.add(b)
    session.commit()

    assert [x.id for x in a.path_components] == [a.id]
    assert [x.id for x in b.path_components] == [a.id, b.id]

    assert b.path == 'a/b'


def test_cte(session):
    if (session.bind.dialect.name == 'sqlite' and
            session.bind.dialect.server_version_info < (3, 8, 3)):
        pytest.skip("Sqlite too old")

    a = Path(basename='a')
    b = Path(basename='b', parent=a)
    c = Path(basename='c', parent=b)
    session.add(c)
    session.commit()

    assert c.parent_id is not None
    assert c.parent_id == b.id
    assert b.parent_id == a.id
    assert a.parent_id is None

    q = session.query(path_closure)

    r = q.all()

    assert (a.id, a.id, 0) in r
    assert (b.id, b.id, 0) in r
    assert (c.id, c.id, 0) in r

    assert (b.id, a.id, 1) in r

    assert (c.id, b.id, 1) in r
    assert (c.id, a.id, 2) in r

def test_path_basename(session):
    a = Path(basename='a')
    b = Path(basename='b', parent=a)

    session.add(b)
    session.commit()

    assert b.path == 'a/b'
    
