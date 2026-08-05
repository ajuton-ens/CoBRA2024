import threading
import socket
import time

class Serveur(threading.Thread):
    def __init__(self, recv_donnee, send_donnee):
        super().__init__()
        adresse_socket = ("", 8081)
        self.socket_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_serveur.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket_serveur.bind(adresse_socket)
        self.socket_serveur.listen(1)
        self.recv_donnee = recv_donnee
        self.recv_donnee.keys()
        self.send_donnee = send_donnee
        self.buffer = ""
        self.client = None
        self.t0 = time.time()
        self.send_delta_T = 0.05
        self.running_send_donnee = False
        self.new_data = True    # savoir quand le serveur à de nouvelle
        self.new_donnee = True   # savoir quand le Cobra à de nouvelle donnee à envoyer
        self.new_data_type = []
        self.running = True

    def run(self):
        while self.running:
            print("en attente d'un client...")
            self.client, client_addr = self.socket_serveur.accept()
            print("client connecté : " + str(client_addr))
            self.t0 = time.time()
            self.running_send_donnee = True
            thread_send = threading.Thread(target=self.sendDonnee)
            thread_send.start()
            while self.running:
                try: data = self.client.recv(1024)
                except: break
                if not data: break
                data = data.decode("utf-8")

                self.buffer += data

                while len(self.buffer) > 0:
                    indice_begin_tram = self.buffer.find("$")
                    indice_end_tram = self.buffer.find("§")

                    if indice_begin_tram == -1:
                        self.buffer = ""
                        break

                    if indice_end_tram == -1:
                        break

                    if indice_begin_tram > indice_end_tram:
                        self.buffer = self.buffer[indice_begin_tram:]
                        continue

                    trame = self.buffer[indice_begin_tram + 1:indice_end_tram]
                    self.buffer = self.buffer[indice_end_tram:]
                    
                    for key in self.recv_donnee.keys():
                        if key in trame[:len(key)]:
                            if key[:3] == "PID":
                                PID_param_list = trame[len(key)+1:].split(";")
                                i = 0
                                for key_PID in self.recv_donnee[key].keys():
                                    self.recv_donnee[key][key_PID] = float(PID_param_list[i])
                                    i += 1
                                    print(self.recv_donnee[key][key_PID])
                                self.new_data_type.append(trame[:len(key)])
                            elif key[:1] == "c":
                                self.recv_donnee[key] = trame[len(key)+1:]
                                print(self.recv_donnee[key])
                                self.new_data_type.append(trame[:len(key)])
                            else:
                                self.recv_donnee[key] = float(trame[len(key)+1:])
                                print(self.recv_donnee[key])
                                self.new_data_type.append(trame[:len(key)])
                    self.new_data = True
            self.running_send_donnee = False
            thread_send.join()
            print("client déco !!!")


    def sendDonnee(self):
        while self.running_send_donnee:
            time.sleep(self.send_delta_T)
            
            while not self.new_donnee: pass
            self.new_donnee = False

            
            data = "t:" + str(round(time.time() - self.t0, 2)) + ";"

            for key, value in self.send_donnee.items():
                data += str(key) + ":" + str(round(value, 6)) + ";"

            s = "$" + data[:-1] + "§"
            try: self.client.sendall(s.encode("utf-8"))
            except:
                print("flux non envoyer")
                break



    def Stop(self):
        self.running = False
        self.running_send_donnee = False