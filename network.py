import socket


class Network:

    def __init__(self, hoster):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = "127.0.0.1"
        self.hoster = hoster
        self.port = 4050
        self.addr = (self.host, self.port)
        self.id = self.connect()

    def connect(self):
        if not self.hoster:
            self.host = "130.208.243.61"
            self.port = 4050
            self.addr = (self.host, self.port)

        self.client.connect(self.addr)
        return self.client.recv(2048).decode()

    def send(self, data):
        """
        :param data: str
        :return: str
        """
        try:
            self.client.send(str.encode(data))
            reply = self.client.recv(2048).decode()
            return reply
        except socket.error as e:
            return str(e)