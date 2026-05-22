from tkinter import *
from tkinter import ttk
import json
import pid_fenetre
import client
import  graphe
import time



class Fenetre(Tk):
    def __init__(self):
        super().__init__()



        #self.geometry("1100x600")
        self.title("Fenetre")
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.resizable(True, True)

        frame_control = ttk.Frame(self)

        fram_connection = ttk.Frame(frame_control)
        ttk.Label(fram_connection, text="connection CoBar :").pack()
        fram_connection_entry = ttk.Frame(fram_connection)

        ttk.Label(fram_connection_entry, text="ip :").grid(row=1, column=0)
        self.ip_entry = StringVar()
        ttk.Entry(fram_connection_entry, textvariable=self.ip_entry, width=15).grid(row=1, column=1)
        ttk.Label(fram_connection_entry, text="port :").grid(row=2, column=0)
        self.port_entry = StringVar()
        ttk.Entry(fram_connection_entry, textvariable=self.port_entry, width=6).grid(row=2, column=1)
        fram_connection_entry.pack()

        self.button_connection = ttk.Button(fram_connection, command=self.connection, text="connect")
        self.button_connection.pack()
        fram_connection.pack(side="top", pady=5)

        self.client = client.Client(self.button_connection)


        fram_consigne = ttk.Frame(frame_control)

        self.etas_controle = IntVar()
        self.etas_controle.set(0)
        def activeControle():
            if self.etas_controle.get():
                l = ["etas_alt:"+str(self.etas_alt.get()), "etas_angle:"+str(self.etas_angle.get()), "etas_pos:"+str(self.etas_pos.get())]
                self.etas_alt_Check.config(state="normal")
                self.etas_angle_Check.config(state="normal")
                self.etas_pos_Check.config(state="normal")
                # self.Check_manuel_control.config(state="disabled")
                # self.etas_manuel_control.set(0)
                manuel_control()

            else:
                l = ["etas_alt:0", "etas_angle:0", "etas_pos:0"]
                self.etas_alt_Check.config(state="disabled")
                self.etas_angle_Check.config(state="disabled")
                self.etas_pos_Check.config(state="disabled")
                # self.Check_manuel_control.config(state="normal")

            self.client.Sends(l)

        ttk.Checkbutton(fram_consigne, text="active contrôle", variable=self.etas_controle, command=activeControle).pack()


        ttk.Label(fram_consigne, text="consignes :").pack()
        fram_consigne_entry = ttk.Frame(fram_consigne)

        ttk.Label(fram_consigne_entry, text="altitude :").grid(row=0, column=0)
        self.alt_entry = DoubleVar()
        ttk.Spinbox(fram_consigne_entry, textvariable=self.alt_entry, from_=0, to=10, width=6, format="%.2f", increment=0.5).grid(row=0, column=1)
        self.alt_entry.set(1.0)
        ttk.Button(fram_consigne_entry, command=lambda : self.client.Send("alt:"+str(round(self.alt_entry.get(), 2))), text="send").grid(row=0, column=2)

        ttk.Label(fram_consigne_entry, text="angle :").grid(row=1, column=0, pady=10)
        self.angle_entry = DoubleVar()
        ttk.Spinbox(fram_consigne_entry, textvariable=self.angle_entry, from_=-180, to=180, width=6, increment=10).grid(row=1, column=1)
        self.angle_entry.set(0)
        ttk.Button(fram_consigne_entry, command=lambda : self.client.Send("angle:"+str(round(self.angle_entry.get(), 2))), text="send").grid(row=1, column=2)

        ttk.Label(fram_consigne_entry, text="pos (x, y) :").grid(row=2, column=0, pady=0)

        self.x_entry = DoubleVar()
        self.y_entry = DoubleVar()
        fram_pos_entry = ttk.Frame(fram_consigne_entry)
        ttk.Spinbox(fram_pos_entry, textvariable=self.x_entry, from_=0, to=50, width=4, increment=1).grid(row=0, column=0)
        ttk.Spinbox(fram_pos_entry, textvariable=self.y_entry, from_=0, to=50, width=4, increment=1).grid(row=0, column=1)
        fram_pos_entry.grid(row=2, column=1)
        self.x_entry.set(0)
        self.y_entry.set(0)

        ttk.Button(fram_consigne_entry, command=lambda: self.client.Sends(["x:" + str(round(self.x_entry.get(), 2)), "y:" + str(round(self.y_entry.get(), 2))]), text="send").grid(row=2, column=2)

        fram_consigne_entry.pack()
        fram_consigne.pack(side="top", pady=5)

        fram_pid = ttk.Frame(frame_control)
        ttk.Label(fram_pid, text="PIDs :").pack()
        fram_pid_entry = ttk.Frame(fram_pid)

        ttk.Button(fram_pid_entry, command=lambda : self.OpenPidFenetre("alt"), text="PID altitude").grid(row=0, column=0, pady=5)

        self.etas_alt = IntVar()
        self.etas_alt_Check = ttk.Checkbutton(fram_pid_entry, text="active", variable=self.etas_alt,
                        command=lambda:self.client.Send("etas_alt:"+str(self.etas_alt.get())))
        self.etas_alt_Check.grid(row=0, column=1, padx=5)

        ttk.Button(fram_pid_entry, command=lambda : self.OpenPidFenetre("angle"), text="PID angle").grid(row=1, column=0)

        self.etas_angle = IntVar()
        self.etas_angle_Check = ttk.Checkbutton(fram_pid_entry, text="active", variable=self.etas_angle,
                     command=lambda: self.client.Send("etas_angle:" + str(self.etas_angle.get())))
        self.etas_angle_Check.grid(row=1, column=1)

        ttk.Button(fram_pid_entry, command=lambda: self.OpenPidFenetre("pos"), text="PID pos").grid(row=2, column=0)

        self.etas_pos = IntVar()
        self.etas_pos_Check = ttk.Checkbutton(fram_pid_entry, text="active", variable=self.etas_pos,
                                                command=lambda: self.client.Send(
                                                    "etas_pos:" + str(self.etas_pos.get())))
        self.etas_pos_Check.grid(row=2, column=1)

        self.etas_alt_Check.config(state="disabled")
        self.etas_angle_Check.config(state="disabled")
        self.etas_pos_Check.config(state="disabled")

        fram_pid_entry.pack()

        fram_pid.pack(side="top", pady=5)

        def ListeGrandeur(event):
            self.graphe.changeGrandeur(liste_grandeur.get())

        list_comm = ["altitude", "angle", "x", "y"]
        liste_grandeur = ttk.Combobox(frame_control, values=list_comm, width=10)
        liste_grandeur.pack()
        liste_grandeur.set(list_comm[0])

        liste_grandeur.bind("<<ComboboxSelected>>", ListeGrandeur)

        self.etas_gele = IntVar()
        self.etas_gele.set(0)
        def gele():
            self.graphe.gele = self.etas_gele.get()

        ttk.Checkbutton(frame_control, text="gèle", variable=self.etas_gele, command=gele).pack()

        ttk.Button(frame_control, command=lambda:self.graphe.save_file(), text="save").pack(pady=5)

        self.d_time = 0
        l = ["z", "q", "s", "d", "a", "e", "Shift_L", "Control_L", "r"]
        def key_pressed(event):
            print(event.keysym)
            t = time.time()
            if self.d_time + 0.5 < t:
                self.d_time = t
            else: return

            if event.keysym in l:
                self.client.Send("c:"+event.keysym)


        def manuel_control():
            if self.etas_manuel_control.get():
                self.bind("<Key>", key_pressed)
            else:
                self.unbind("<Key>")


        self.etas_manuel_control = IntVar()
        self.Check_manuel_control = ttk.Checkbutton(frame_control, text="contrôl manuel", variable=self.etas_manuel_control, command=manuel_control)
        self.Check_manuel_control.pack()

        frame_amp = ttk.Frame(frame_control)

        ttk.Label(frame_amp, text="amp :").grid(row=0, column=0, padx=5)

        self.amp = DoubleVar()
        ttk.Spinbox(frame_amp, textvariable=self.amp, from_=0, to=100, width=6,
                    increment=1).grid(row=0, column=1)

        ttk.Button(frame_amp, text="OK",
                   command=lambda: self.client.Send("amp:" + str(round(self.amp.get(), 2)))).grid(row=0, column=2)

        frame_amp.pack(side="top", padx=5, pady=5)

        self.alt_offset = DoubleVar()
        ttk.Spinbox(frame_control, textvariable=self.alt_offset, from_=0, to=100, width=6,
                    increment=1).pack(pady=5)
        ttk.Button(frame_control, text="OK", command=lambda: self.client.Send("offset_alt:"+str(round(self.alt_offset.get(), 2)))).pack()

        frame_control.pack(side="left", fill="x", padx=5, pady=5)

        frame_graphe = ttk.Frame(self)
        frame_graphe.pack(side="right", fill="x", padx=5, pady=5)

        self.graphe = graphe.Graphe(self, frame_graphe, self.client)

        ListeGrandeur(None)

        self.dico_config = {}
        try:
            with open("config.json", "r") as file:
                self.dico_config = json.load(file)
            self.ip_entry.set(self.dico_config["ip"])
            self.port_entry.set(self.dico_config["port"])
        except: pass






    def close(self):

        self.dico_config["ip"] = self.ip_entry.get()
        self.dico_config["port"] = self.port_entry.get()

        with open("config.json", "w") as file:
            json.dump(self.dico_config, file)
        self.client.deconnect()
        self.graphe.Stop()
        self.running_clavier = False
        self.destroy()




    def connection(self):
        if not self.client.is_connected():
            ip = self.ip_entry.get()
            port = self.port_entry.get()
            ret = self.client.Connect(ip, port)
            if ret:
                self.graphe.clearGraph()
                self.graphe.Start()
        else:
            self.client.deconnect()
            self.graphe.Stop()



    def OpenPidFenetre(self, type):
        pidfenetre = pid_fenetre.PIDFenetre(self, type)