from http_server import HttpServer

if __name__ == "__main__":
    http_server = HttpServer("nats://localhost:4222")
    http_server.run("localhost", 8099)
