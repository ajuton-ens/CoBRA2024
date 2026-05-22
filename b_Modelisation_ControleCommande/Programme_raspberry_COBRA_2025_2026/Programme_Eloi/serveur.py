import threading
import socket
import time

PID_ = {"Kp":0, "Ki":0, "Kd":0, "sample_time":0, "filtre_derivee":0, "saturation":0}
donnee = {"alt":0, "angle":0, "etas_alt":0, "etas_angle":0, "etas_pos":0, "PID_alt":PID_.copy(), "PID_angle":PID_.copy(), "c":"", "offset_alt":0, "x":0, "y":0, "amp":0}
mes_donnee = {"alt":78, "angle":0, "alt_cons":0, "angle_cons":0, "alt_force":0, "angle_force":0, "x":1, "y":2, "x_fix":0, "y_fix":0, "angle_fix":0}

class Serveur(threading.Thread):
    def __init__(self, donnee, mes_donnee):
        super().__init__()
        adresse_socket = ("", 8081)
        self.socket_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_serveur.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket_serveur.bind(adresse_socket)
        self.socket_serveur.listen(1)
        self.donnee = donnee
        self.donnee.keys()
        self.mes_donnee = mes_donnee
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
            thread_send = threading.Thread(target=self.send_donnee)
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
                    
                    for key in self.donnee.keys():
                        if key in trame[:len(key)]:
                            if key[:3] == "PID":
                                PID_param_list = trame[len(key)+1:].split(";")
                                i = 0
                                for key_PID in self.donnee[key].keys():
                                    self.donnee[key][key_PID] = float(PID_param_list[i])
                                    i += 1
                                    print(self.donnee[key][key_PID])
                                self.new_data_type.append(trame[:len(key)])
                            elif key[:1] == "c":
                                self.donnee[key] = trame[len(key)+1:]
                                print(self.donnee[key])
                                self.new_data_type.append(trame[:len(key)])
                            else:
                                self.donnee[key] = float(trame[len(key)+1:])
                                print(self.donnee[key])
                                self.new_data_type.append(trame[:len(key)])
                    self.new_data = True
            self.running_send_donnee = False
            thread_send.join()
            print("client déco !!!")


    def send_donnee(self):
        while self.running_send_donnee:
            time.sleep(self.send_delta_T)
            
            while not self.new_donnee: pass
            self.new_donnee = False

            
            data = "t:" + str(round(time.time() - self.t0, 2)) + ";"

            for key, value in self.mes_donnee.items():
                data += str(key) + ":" + str(round(value, 6)) + ";"

            s = "$" + data[:-1] + "§"
            try: self.client.sendall(s.encode("utf-8"))
            except:
                print("flux non envoyer")
                break



    def Stop(self):
        self.running = False
        self.running_send_donnee = False