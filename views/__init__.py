from pyramid.config import Configurator

with Configurator() as config:
    config.add_route('home', '/')
    config.add_route('update_alias', '/update_alias')
    config.include('pyramid_mako')
    config.scan()
    app = config.make_wsgi_app()
