from pyramid.config import Configurator

with Configurator() as config:
    config.add_route('home', '/')
    config.include('pyramid_mako')
    config.scan()
    app = config.make_wsgi_app()
