import main
from gevent.pywsgi import WSGIServer


main.app.run(debug=True)


# http_server = WSGIServer(("0.0.0.0", 8080), main.app)
# http_server.serve_forever()
