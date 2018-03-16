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
import metadb.db as db
import metadb.io as io
import metadb.query as query
import metadb.model as model
import metadb.crawler as crawler
import metadb.util as util
from sqlalchemy.orm import aliased
from sqlalchemy.sql import func
from argparse import ArgumentParser
from inspect import getdoc
import os
import glob
import sys


def cli(argv=sys.argv[1:], session=None):
    """
    Functions to store and retrieve metadata
    """

    parser = ArgumentParser(description=getdoc(cli))
    parser.add_argument('--database',
                        help='Database URL',
                        default='sqlite:///%s/metadb.db' %
                        os.environ.get('HOME', '.'))
    parser.add_argument('--debug',
                        help='Debug mode',
                        action='store_true')

    subparser = parser.add_subparsers(help="Command")

    import_cmd().setup_parser(subparser)
    list_cmd().setup_parser(subparser)
    collection_cmd().setup_parser(subparser)
    collection_report_cmd().setup_parser(subparser)
    crawl_cmd().setup_parser(subparser)

    args = parser.parse_args(argv)

    if session is None:
        db.connect(url=args.database, debug=args.debug, init=True)
        session = db.Session()

    args.command(args, session=session)
    session.commit()


class collection_cmd(object):
    """
    Create a new collection
    """

    def setup_parser(self, subparser):
        parser = subparser.add_parser('collection',
                                      help="Create a collection",
                                      description=getdoc(self))

        parser.add_argument('--name',
                            help="Collection name",
                            )

        parser.set_defaults(command=self)

    def __call__(self, args, session):
        c = model.Collection(name=args.name)
        session.add(c)


class import_cmd(object):
    """
    Import a file's metadata
    """

    def setup_parser(self, subparser):
        parser = subparser.add_parser('import',
                                      help="Import a file's metadata",
                                      description=getdoc(self))

        parser.add_argument('--collection',
                            help="Collection name",
                            action="append",
                            )

        parser.add_argument('file',
                            help="File to add",
                            nargs="+",
                            )

        parser.set_defaults(command=self)

    def __call__(self, args, session):
        colls = (session.query(model.Collection)
                        .filter(model.Collection.name.in_(args.collection)))

        for g in args.file:
            try:
                # Check if this works as a glob
                next(glob.iglob(g, recursive=True))
                for f in glob.iglob(g, recursive=True):
                    io.read_general(f, collections=colls, session=session)
            except (StopIteration, TypeError):
                # Either not a filesystem glob, or using Python < 3.4
                # Try reading it anyway, to support things like opendap links
                io.read_general(g, collections=colls, session=session)


class list_cmd(object):
    """
    List files in the catalogue, filtered by attribute values.

    Attribute constraints may be specified multiple times, resulting in an AND
    """

    def setup_parser(self, subparser):
        parser = subparser.add_parser('list',
                                      help="List files",
                                      description=getdoc(self))

        parser.add_argument('--variable',
                            help="Variable name",
                            action='append')

        parser.add_argument('--file-attribute',
                            help="Global file attribute",
                            nargs=2,
                            metavar=('KEY', 'VALUE'),
                            action='append')

        parser.add_argument('--var-attribute',
                            help="Variable attribute",
                            nargs=2,
                            metavar=('KEY', 'VALUE'),
                            action='append')

        parser.set_defaults(command=self)

    def __call__(self, args, session):
        sub = query.search_metadata(session,
                                    variables=args.variable,
                                    file_attributes=args.file_attribute,
                                    variable_attributes=args.var_attribute)
        sub = sub.subquery()
        sub = aliased(model.Metadata, sub)

        # Convert the Metadata into path, title tuples
        attr_title = aliased(model.Attribute)
        q = (session
             .query(model.Path.path, attr_title.value)
             .join(sub, model.Path.meta)
             .join(attr_title, sub.attributes)
             .filter(attr_title.key == 'title')
             )

        for path, title in q:
            print(path, '|', title)


class crawl_cmd(object):
    """
    Crawl the filesystem to update the database
    """

    def setup_parser(self, subparser):
        parser = subparser.add_parser('crawl',
                                      help="Crawl the filesystem",
                                      description=getdoc(self))

        parser.add_argument(
                'root',
                help='Root path'
                )

        parser.add_argument(
                '--collection',
                help='Collection name'
                )

        parser.set_defaults(command=self)

    def __call__(self, args, session):
        c = (session.query(model.Collection)
                        .filter(model.Collection.name == args.collection)
                        .one())

        crawler.crawl_recursive(session, args.root, collection=c)


class collection_report_cmd(object):
    """
    Print information about a collection
    """
    def setup_parser(self, subparser):
        parser = subparser.add_parser('collection report',
                                      help="Print collection info",
                                      description=getdoc(self))

        parser.add_argument(
                '--collection',
                help='Collection name'
                )

        parser.set_defaults(command=self)

    def __call__(self, args, session):
        from .model import Collection, Path
        import pwd
        q = (session.query(Collection.name, Path.uid, func.sum(Path.size))
                .join(Collection.paths)
                .group_by(Collection.name, Path.uid)
                .filter(Path.uid is not None)
                )
        for n, u, s in q:
            p = pwd.getpwuid(u)
            print(n, p.pw_gecos, p.pw_name, util.size_str(s))

