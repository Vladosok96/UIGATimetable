import main
from gevent.pywsgi import WSGIServer

http_server = WSGIServer(("127.0.0.1", 8080), main.app)
http_server.serve_forever()
