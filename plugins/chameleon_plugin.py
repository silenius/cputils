# -*- coding: utf-8 -*-

import os
import os.path

from cherrypy.process import plugins
from chameleon import PageTemplateLoader

__all__ = ['ChameleonTemplatePlugin']


class ChameleonTemplatePlugin(plugins.SimplePlugin):

    def __init__(self, bus, config):
        super(ChameleonTemplatePlugin, self).__init__(bus)
        self.config = config

    def start(self):
        self.bus.log('ChameleonTemplatePlugin: Starting template engine')

        loader_config = {}
        loader_search_path = self.config.get('loader.search_path')
        loader_default_extension = self.config.get('loader.default_extension')

        for (key, value) in self.config.iteritems():
            key_without_prefix = key.rsplit('.')[-1]
            if key.startswith('chameleon.config.'):
                os.environ['CHAMELEON_%s' % key_without_prefix.upper()] = value
            elif key.startswith('loader.config.'):
                loader_config[key_without_prefix] = value

        self.loader = PageTemplateLoader(loader_search_path,
                                         loader_default_extension,
                                         **loader_config)

        self.bus.subscribe('lookup-template', self.get_template)

    def stop(self):
        self.bus.log('ChameleonTemplatePlugin: Stopping template engine')
        self.bus.unsubscribe('lookup-template', self.get_template)

    def get_template(self, filename, format=None):
        return self.loader.load(filename, format)
