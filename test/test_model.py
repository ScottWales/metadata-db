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


def test_db(session):
    q = session.query(Metadata)
    assert q.count() == 0


def test_collection(session):
    c = Collection(name='c')
    p = Path(collections=set((c,)))
    session.add(p)

    q = (session.query(Path)
                .join(Path.collections)
                .filter(Collection.name == 'c')
                .one())
    assert q == p


def test_path(session):
    p = Path(path='/foo/bar')
    session.add(p)

    m = Metadata(paths=[p])
    session.add(m)

    assert p.basename == 'bar'

    path, meta = session.query(Path, Metadata).join(Path.meta).one()


def test_path_closure(session):
    a = Path(basename_='a')

    b = Path(basename_='b', parent=a)
    session.add(b)
    session.commit()

    assert [x.id for x in a.path_components] == [a.id]
    assert [x.id for x in b.path_components] == [a.id, b.id]

def test_cte(session):
    a = Path(basename_='a')
    b = Path(basename_='b', parent=a)
    c = Path(basename_='c', parent=b)
    session.add(c)
    session.commit()

    assert c.parent_id is not None
    assert c.parent_id == b.id
    assert b.parent_id == a.id
    assert a.parent_id is None

    q = session.query(path_closure)

    r = q.all()

    assert (a.id,a.id,0) in r
    assert (b.id,b.id,0) in r
    assert (c.id,c.id,0) in r

    assert (b.id,a.id,1) in r

    assert (c.id,b.id,1) in r
    assert (c.id,a.id,2) in r

