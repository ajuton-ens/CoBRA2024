import socket
import time
import threading

class Client():
    def __init__(self, button_connection):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(1)
        self.connected = False
        self.button_connection = button_connection
        self.i = 0
        self.max_iter = 20


    def Connect(self, ip, port):
        if self.sock:
            self.sock.close()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try: self.sock.connect((ip, int(port)))
        except:
            print("Connection impossible...")
            self.connected = False
            return 0
        print("Le client est connecté au serveur")
        self.connected = True
        self.button_connection.config(text="déconnect")
        return 1

    def deconnect(self):
        self.connected = False
        self.button_connection.config(text="connect")
        if self.sock:
            self.sock.close()




    def Sends(self, data_list):
        data = ""
        for d in data_list:
            data += d + "§$"

        return self.Send(data[:-2])

    def Send(self, data):
        print(data)
        s = "$" + data + "§"
        try: self.sock.send(s.encode("utf8"))
        except: print("commande non envoyer")


    def Resv(self):
        if not self.connected:
            return None
        try:
            ret = self.sock.recv(1024).decode("utf8")
            self.i = 0
            return ret

        except:
            if self.connected:
                print("flux non reçu")
                self.i += 1
                if self.i > self.max_iter:
                    self.i = 0
                    self.deconnect()
            return None



    def is_connected(self):
        try:
            self.sock.getpeername()
            self.connected = True
            return True
        except OSError:
            self.connected = False
            return False