# -*- coding: utf-8 -*-

import cherrypy

__all__ = ['SATool']


class SATool(cherrypy.Tool):

    def __init__(self):
        super(SATool, self).__init__('on_start_resource', self.bind_session,
                                     priority=20)
        self.session = None

    def _setup(self):
        super(SATool, self)._setup()
        cherrypy.request.hooks.attach('on_end_resource',
                                      self.remove_session, priority=80)

    def bind_session(self):
        self.session = cherrypy.engine.publish('get-session').pop()

    def remove_session(self):
        if not self.session:
            return

        self.session.remove()
        self.session = None
