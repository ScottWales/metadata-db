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

def test_crawler(session, tmpdir):
    c = Collection(name='c')
    session.add(c)

    # Create a test file and crawl the directory
    a = tmpdir.join('a')
    a.write('hello')
    crawl_recursive(session, tmpdir, collection=c)

    # There should be an entry for the test file
    p = session.query(Path).filter(Path.path == str(a)).one()
    assert p.size == len('hello')

    # There should be one path
    assert session.query(Path).count() == 1

    # Create a new file
    b = tmpdir.join('b')
    b.write('hello')
    crawl_recursive(session, tmpdir, collection=c)

    # There should now be two paths present
    assert session.query(Path).count() == 2

    # Update an existing file
    a.write('goodbye')
    crawl_recursive(session, tmpdir, collection=c)

    p = session.query(Path).filter(Path.path == str(a)).one()
    assert p.size == len('goodbye')
