from wsgiref.simple_server import make_server
from views import app
from simple_settings import settings

server = make_server(settings.SERVER_URL, settings.SERVER_PORT, app)
print('Serving at %s:%d' % (settings.SERVER_URL, settings.SERVER_PORT))
server.serve_forever()