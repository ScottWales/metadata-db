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
from metadb.query import *
from metadb.model import *


def test_search_metadata(session):
    # Basic sample data
    ma = Metadata()
    va1 = Variable(name='1', meta=ma)
    va2 = Variable(name='2', meta=ma)

    mb = Metadata()
    vb1 = Variable(name='1', meta=mb)

    session.add_all([ma, va1, va2, mb, vb1])

    # Query by variable
    q = search_metadata(session, variables=['1'])
    assert q.count() == 2

    q = search_metadata(session, variables=['2'])
    assert q.count() == 1

    # Add some attrs
    a1 = Attribute(key='a', value='v')
    va1.attributes.set(a1)

    mb.attributes.set(a1)

    q = search_metadata(session, file_attributes=[('a', 'v')])
    assert q.count() == 1
    assert q.one() == mb

    q = search_metadata(session, variable_attributes=[('a', 'v')])
    assert q.count() == 1
    assert q.one() == ma
