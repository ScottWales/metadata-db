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


def test_collection_cmd(session):
    cli(argv='collection --name a'.split(), session=session)

    q = session.query(Collection).one()
    assert q.name == 'a'


def test_import_to_collection(session):
    c = Collection(name='a')
    session.add(c)

    cli(argv='import --collection a foo'.split(), session=session)

    q = session.query(Path).one()
    assert q.collections == [c]
