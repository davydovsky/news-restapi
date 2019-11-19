from news_restapi.server import rest_server


def start_server():
    rest_server(8080)


if __name__ == '__main__':
    start_server()
