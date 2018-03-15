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

from metadb.web import *
import metadb.model as model
import pytest

@pytest.fixture(scope='session')
def test_app():
    app.testing = True
    app.config['DB'] = 'sqlite:///:memory:'
    a = app.test_client()
    yield a


@pytest.fixture
def session(test_app):
    with app.app_context():
        get_db()

        yield Session


def test_root(test_app):
    r = test_app.get('/')
    assert r.data.decode('utf-8') == 'hello'


def test_list_collections(test_app, session):
    c = model.Collection(name='foo')
    session.add(c)

    r = test_app.get('/collection')
    assert 'foo' in r.data.decode('utf-8')


def test_show_collection(test_app, session):
    c = model.Collection(name='foo')
    session.add(c)

    pa = model.Path(path='/path/a')
    pb = model.Path(path='/path/b')
    c.paths = [pa, pb]

    r = test_app.get('/collection/foo')
    assert 'foo' in r.data.decode('utf-8')
    assert '/path/a' in r.data.decode('utf-8')


def test_db_clear(test_app, session):
    assert session.query(Collection).count() == 0
