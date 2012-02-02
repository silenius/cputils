# -*- coding: utf-8 -*-

from cherrypy.process import plugins

from sqlalchemy import engine_from_config, MetaData, __version__ as sa_version
from sqlalchemy.orm import scoped_session, sessionmaker

__all__ = ['SAEnginePlugin']

if sa_version.split('.') < ['0', '7', '4']:
    raise ImportError('Version 0.7.4 or later of SQLAlchemy required.')

class SAEnginePlugin(plugins.SimplePlugin):
    """
        SQLAlchemy integration for CherryPy
        ===================================

        Usage:

        In your application configuration:

        [sqlalchemy]

        engine.url = "postgresql+psycopg2://user:password@host/db"
        engine.echo = False
        engine.echo_pool = False
        engine.pool_size = 5
        engine.pool_timeout = 30
        engine.pool_recycle = -1
        engine.max_overflow = 10
        engine.convert_unicode = False
        metadata.reflect = False
        metadata.schema = None
        metadata.quote_schema = None
        session.autocommit = False
        session.autoflush = True
    """

    def __init__(self, bus, config, engine=None, session=None, meta=None):
        super(SAEnginePlugin, self).__init__(bus)

        self.sa_engine = engine
        self.sa_meta = meta
        self.config = config

        self.sa_session = session if session else scoped_session(
                          sessionmaker(autoflush=True, autocommit=False))

        self.bus.subscribe('get-session', self.get_session)

    def start(self):
        self.bus.log('SAEnginePlugin: Starting up DB access')

        # Engine

        if not self.sa_engine:
            self.sa_engine = engine_from_config(self.config, prefix='engine.')

        # Metadata

        if not self.sa_meta:
            metadata_config = dict((k.lstrip('metadata.'), v) for (k, v) in\
                                   a.iteritems() if k.startswith('metadata.'))
            self.sa_meta = MetaData(engine=self.sa_engine, **metadata_config)
        else:
            self.sa_meta.bind = self.sa_engine

        # Session

        self.sa_meta.bind = self.sa_engine
        self.sa_session.configure(bind=self.sa_engine)

        if self.config.get('metadata.reflect'):
            self.sa_meta.reflect()

    def stop(self):
        self.bus.log('SAEnginePlugin: Stopping down DB access')
        self.bus.unsubscribe('get-session', self.get_session)

        if self.sa_engine:
            self.sa_engine.dispose()
            self.sa_engine = None

    def get_session(self):
        return self.sa_session

