from http_server import HttpServer

if __name__ == "__main__":
    http_server = HttpServer(
        auth_nats_url="nats://localhost:4222", 
        user_nats_url="nats://localhost:4222",
        password_salt="password_salt")
    http_server.run("localhost", 8099)
