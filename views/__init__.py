from pyramid.config import Configurator

with Configurator() as config:
    config.add_route('home', '/')
    config.scan()
    app = config.make_wsgi_app()
