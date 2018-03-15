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
from flask import Flask, g, render_template
import metadb.db as db
from metadb.model import *
from sqlalchemy.orm import scoped_session

class DefaultConfig(object):
    DEBUG = False
    TESTING = False
    DB = 'sqlite:////home/unimelb.edu.au/swales/metadb.db'

app = Flask(__name__)
app.config.from_object('metadb.web.DefaultConfig')
# app.config.from_envvar('METADB_SETTINGS')

Session = scoped_session(db.Session)


def get_db():
    if not hasattr(g, 'db'):
        g.db = db.connect(app.config['DB'], init=True, session=Session)
    return g.db


@app.teardown_appcontext
def shutdown_session(exception=None):
    Session.remove()


@app.route('/')
def hello():
    return 'hello'


@app.route('/collection')
def list_collections():
    get_db()
    collections = Session.query(Collection)
    return render_template('collection.html', collections=collections)


@app.route('/collection/<collection>')
def show_collection(collection):
    get_db()
    collection = Session.query(Collection).filter(Collection.name == collection).one()
    return render_template('show_collection.html', collection=collection)


@app.route('/path/<path_id>')
def show_path(path_id):
    get_db()
    path, meta = Session.query(Path, Metadata).join(Path.meta).filter(Path.id == path_id).one()
    return render_template('show_path.html', path=path, meta=meta)
