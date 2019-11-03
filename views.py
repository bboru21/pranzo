from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response
from simple_settings import settings

def hello_world(request):
    return Response('Hello World')

if __name__ == '__main__':
    with Configurator() as config:
        config.add_route('hello', '/')
        config.add_view(hello_world, route_name='hello')
        app = config.make_wsgi_app()
    server = make_server(settings.SERVER_URL, settings.SERVER_PORT, app)
    print('Serving at %s:%d' % (settings.SERVER_URL, settings.SERVER_PORT))
    server.serve_forever()