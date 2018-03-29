#!/usr/bin/env python
# Copyright 2018 Scott Wales
#
# author: Scott Wales <scottwales@outlook.com.au>
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


"""
Connect to the database and manage sessions

.. py:class:: Session

    The database session factory, an instance of
    :py:meth:`sqlalchemy.orm.session.sessionmaker`
"""

from __future__ import print_function
import sqlalchemy
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from .model import Base
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.environment import EnvironmentContext

Session = sessionmaker()


def connect(url, debug=False, init=False, session=Session):
    """connect(url, debug=False, init=False, session=Session)
    Connect to the database and initialise the Session

    :param str url: Database URL to connect to (SQLAlchemy style)
    :param bool debug: Print database logs
    :param bool init: Initialise the database (requires write permissions)
    :param session: SQLAlchemy sessionmaker to bind to the engine

    :return: A connection to the database
    :rtype: :py:class:`sqlalchemy.engine.Connection`
    """
    engine = create_engine(url, echo=debug)

    if engine.dialect.name == 'sqlite':
        # Enable transactions
        @event.listens_for(engine, "connect")
        def do_connect(dbapi_connection, connection_record):
            # disable pysqlite's emitting of the BEGIN statement entirely.
            # also stops it from emitting COMMIT before any DDL.
            dbapi_connection.isolation_level = None

        @event.listens_for(engine, "begin")
        def do_begin(conn):
            # emit our own BEGIN
            conn.execute("BEGIN")

    if init:
        try:
            apply_migrations(engine)
        except sqlalchemy.exc.OperationalError:
            raise IOError("Database version incompatible")

    session.configure(bind=engine)

    return engine

def apply_migrations(engine):
    """
    Apply Alembic migrations to the connected database
    """
    target = 'head'

    config = Config()
    config.set_main_option("script_location", "alembic")
    script = ScriptDirectory.from_config(config)

    def upgrade_fn(rev, context):
        return script._upgrade_revs(target, rev)

    with EnvironmentContext(config, script) as env:
        with engine.connect() as conn:
            env.configure(conn, fn=upgrade_fn, destination_rev=target)

            with env.begin_transaction():
                env.run_migrations()

