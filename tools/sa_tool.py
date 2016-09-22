# -*- coding: utf-8 -*-

import cherrypy

__all__ = ['SATool']


class SATool(cherrypy.Tool):

    def __init__(self):
        super(SATool, self).__init__('on_start_resource', self.bind_session,
                                     priority=20)

    def _setup(self):
        super(SATool, self)._setup()
        cherrypy.request.hooks.attach('on_end_resource',
                                      self.remove_session, priority=80)

    def bind_session(self):
        cherrypy.request.db = cherrypy.engine.publish('get-session').pop()

    def remove_session(self):
        cherrypy.request.db = None
        cherrypy.engine.publish('release-session')
