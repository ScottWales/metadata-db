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
from metadb.crawler import *
from metadb.model import Collection, Path


def test_crawler_updates(session, tmpdir):
    c = Collection(name='c')
    session.add(c)
    p = Path(basename=str(tmpdir))
    session.add(p)

    # Create a test file and crawl the directory
    a = tmpdir.join('a')
    a.write('hello')
    crawl_recursive(session, str(tmpdir), collection=c)

    # There should be an entry for the test file
    p = session.query(Path).filter(Path.path == str(a)).one()
    assert p.size == len('hello')
    assert c in p.collections
    last_seen = p.last_seen

    # There should be two paths
    assert session.query(Path).count() == 2

    # Create a new file
    b = tmpdir.join('b')
    b.write('hello')
    crawl_recursive(session, str(tmpdir), collection=c)

    # There should now be three paths present
    assert session.query(Path).count() == 3

    # Update an existing file
    a.write('goodbye')
    crawl_recursive(session, str(tmpdir), collection=c)

    p = session.query(Path).filter(Path.path == str(a)).one()

    # The size should have changed
    assert p.size == len('goodbye')
    assert p.last_seen > last_seen


def test_crawler_recursive(session, tmpdir):
    col = Collection(name='c')
    session.add(col)
    p = Path(basename=str(tmpdir))
    session.add(p)

    a = tmpdir.mkdir('a')
    b = a.join('b')
    c = tmpdir.mkdir('c')
    b.write('hello')

    crawl_recursive(session, str(tmpdir), collection=col)
    assert session.query(Path).count() == 4


def test_crawler_errors(session, tmpdir):
    col = Collection(name='c')
    session.add(col)
    p = Path(basename=str(tmpdir))
    session.add(p)

    a = tmpdir.mkdir('a')

    # Unreadable file
    b = a.join('b')
    b.write('hello')
    b.chmod(0000)

    # Link to nowhere
    c = a.join('c')
    c.mksymlinkto('nowhere')

    crawl_recursive(session, str(tmpdir), collection=col)
