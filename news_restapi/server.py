import http.server
import importlib
import json
import re
import sys

from news_restapi import exceptions
from news_restapi.controllers import NewsController, CommentController
from news_restapi.repositories import NewsRepository, CommentRepository

importlib.reload(sys)


def service_worker():
    pass


news_controller = NewsController(NewsRepository())
comment_controller = CommentController(CommentRepository())


routes = {
    r'^/news/$': {
        'GET': news_controller.list_news,
        'POST': news_controller.add_news,
        'media_type': 'application/json'
    },
    r'^/news/(?P<pk>\d+)/$': {
        'GET': news_controller.get_news,
        'PUT': news_controller.update_news,
        'DELETE': news_controller.delete_news,
        'media_type': 'application/json'
    },
    r'^/news/(?P<news_pk>\d+)/comments/$': {
        'GET': comment_controller.list_comments,
        'POST': comment_controller.add_comment,
        'media_type': 'application/json'
    },
    r'^/news/(?P<news_pk>\d+)/comments/(?P<pk>\d+)/$': {
        'GET': comment_controller.get_comment,
        'PUT': comment_controller.update_comment,
        'DELETE': comment_controller.delete_comment,
        'media_type': 'application/json'
    }
}

poll_interval = 0.1


class RESTRequestHandler(http.server.BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.routes = routes
        http.server.BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

    def do_HEAD(self):
        self.handle_method('HEAD')

    def do_GET(self):
        self.handle_method('GET')

    def do_POST(self):
        self.handle_method('POST')

    def do_PUT(self):
        self.handle_method('PUT')

    def do_DELETE(self):
        self.handle_method('DELETE')

    def get_payload(self):
        payload_len = int(self.headers.get('content-length', 0))
        payload = self.rfile.read(payload_len)
        payload = json.loads(payload.decode())
        return payload

    def handle_method(self, method):
        try:
            route, params = self.get_route()
            if route is None:
                self.send_response(404)
                self.end_headers()
                self.wfile.write('Route not found'.encode())
            else:
                if method == 'HEAD':
                    self.send_response(200)
                    if 'media_type' in route:
                        self.send_header('Content-type', route['media_type'])
                    self.end_headers()
                else:
                    if method in route:
                        content = route[method](self, **params)
                        if content is not None:
                            self.send_response(200)
                            if 'media_type' in route:
                                self.send_header('Content-type', route['media_type'])
                            self.end_headers()
                            if method != 'DELETE':
                                self.wfile.write(json.dumps(content, sort_keys=True, default=str).encode())
                        else:
                            self.send_response(404)
                            self.end_headers()
                            self.wfile.write('Not found'.encode())
                    else:
                        self.send_response(405)
                        self.end_headers()
                        self.wfile.write('{} is not supported'.format(method).encode())
        except (exceptions.ValidationError, exceptions.NotFoundError) as e:
            self.send_response(e.status_code)
            self.end_headers()
            self.wfile.write(str(e).encode())
        except:
            self.send_response(500)
            self.end_headers()
            self.wfile.write('Internal server error'.format(method).encode())

    def get_route(self):
        for path, route in self.routes.items():
            match = re.match(path, self.path)
            if match:
                params = match.groupdict()
                return route, params
        return None, None


def rest_server(port: int) -> None:
    """
    Starts the REST server
    :param port:
    :return:
    """
    http_server = http.server.HTTPServer(('', port), RESTRequestHandler)
    http_server.service_actions = service_worker
    try:
        http_server.serve_forever(poll_interval)
    except KeyboardInterrupt:
        pass
    http_server.server_close()
