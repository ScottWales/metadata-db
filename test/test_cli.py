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
from metadb.cli import cli
from metadb.model import *
import pytest

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


@pytest.fixture(scope='module')
def sample_data(tmpdir_factory):
    data = tmpdir_factory.mktemp('cli_data')
    a = data.join('a')
    a.write('hello')
    return data


def test_collection_create_cmd(session):
    cli(argv='create --collection a'.split(), session=session)

    q = session.query(Collection).one()
    assert q.name == 'a'

    cli(argv='create -c a'.split(), session=session)

    q = session.query(Collection)
    assert q.count() == 1

    cli(argv='create -c b /root/path /another/path'.split(), session=session)
    q = session.query(Collection).filter_by(name='b').one()

    assert len(q.root_paths) == 2


def test_import_to_collection(session):
    c = Collection(name='a')
    session.add(c)

    cli(argv='import --collection a foo'.split(), session=session)

    q = session.query(Path).one()
    assert q.collections == set((c,))


def test_crawler(session, sample_data):
    with patch('metadb.cli.crawler.crawl_recursive') as crawler:
        cli(argv=('create --collection a %s' %
                  (sample_data)).split(), session=session)
        c = session.query(Collection).one()

        cli(argv='crawl --collection a'.split(), session=session)
        crawler.assert_called_once_with(
            session, str(sample_data), collection=c)

        crawler.reset_mock()

        cli(argv='crawl'.split(), session=session)
        crawler.assert_called_once_with(
            session, str(sample_data), collection=c)


def test_report(session, capsys, sample_data):
    cli(argv=('create --collection a %s' % sample_data).split(), session=session)
    cli(argv='crawl'.split(), session=session)
    cli(argv='report'.split(), session=session)
