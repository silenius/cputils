# -*- coding: utf-8 -*-

from cherrypy.process import plugins

from sqlalchemy import create_engine, MetaData, __version__ as sa_version
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

        In your code:

        SAEnginePlugin(cherrypy.engine, app.config['sqlalchemy'], myengine,
                       mysession, mymeta).subscribe()
    """

    def __init__(self, bus, config, engine=None, session=None, meta=None):
        super(SAEnginePlugin, self).__init__(bus)

        self.sa_engine = engine
        self.sa_meta = meta
        self.sa_session = session
        self.config = config

        self.bus.subscribe('get-session', self.get_session)

    def start(self):
        self.bus.log('SAEnginePlugin: Starting up DB access')

        _config = {}

        for (k, v) in self.config.iteritems():
            _partition = k.partition('.')
            _config.setdefault(_partition[0], {})[_partition[2]] = v

        # Engine

        if not self.sa_engine:
            url = _config['engine'].pop('url')
            self.sa_engine = create_engine(url, **_config['engine'])

        # Metadata

        if not self.sa_meta:
            self.sa_meta = MetaData(bind=self.sa_engine,
                                    **_config.get('metadata', {}))
        elif not self.sa_meta.is_bound():
            self.sa_meta.bind = self.sa_engine
            if _config.get('metadata', {}).get('reflect'):
                self.sa_meta.reflect()

        # Session

        if not self.sa_session:
            _session = sessionmaker(**_config.get('session', {}))
            self.sa_session = scoped_session(_session)

        self.sa_session.configure(bind=self.sa_engine)

    def stop(self):
        self.bus.log('SAEnginePlugin: Stopping down DB access')
        self.bus.unsubscribe('get-session', self.get_session)

        if self.sa_engine:
            self.sa_engine.dispose()
            self.sa_engine = None

    def get_session(self):
        return self.sa_session
