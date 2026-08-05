import socket
import os
import threading
import json


class PosCamFix(threading.Thread):
    def __init__(self):
        super().__init__()
        adresse_socket = ("", 8082)
        self.socket_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_serveur.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket_serveur.bind(adresse_socket)
        self.socket_serveur.listen(1)
        self.running = True

        self.x0 = 0
        self.y0 = 0
        self.z0 = 0
        self.theta = 0

    def run(self):
        while self.running:
            print("en attente d'un client pos cam fix...")
            client, client_addr = self.socket_serveur.accept()
            print("client pos cam fix connecté : " + str(client_addr))
            client.send(("Serveur a client : j'utilise le PID" + str(os.getpid())).encode("utf-8"))

            while self.running:
                try:
                    data = client.recv(4096)
                except:
                    break
                if not data:
                    break
                data = data.decode("utf-8")

                try:
                    data_json = json.loads(data)
                except:
                    continue

                self.x0 = data_json["x"]
                self.y0 = data_json["y"]
                self.z0 = data_json["z"]
                self.theta = data_json["theta"]

    def get_pose(self):
        return self.x0, self.y0, self.z0, self.theta

    def Stop(self):
        self.running = False
        self.socket_serveur.close()
