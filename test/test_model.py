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
