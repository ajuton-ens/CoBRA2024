from tkinter import *
from tkinter import ttk





class PIDFenetre(Toplevel):
    def __init__(self, parent, type):
        super().__init__(parent)
        self.parent = parent

        self.type = type

        self.title("PIDFenetre - "+self.type)
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.resizable(True, True)

        ttk.Label(self, text="PIDs : "+self.type, font=("Arial", 20)).pack(side="top")

        fram_pid = ttk.Frame(self)
        ttk.Label(fram_pid, text="Kp :").grid(row=0, column=0, pady=2)
        self.Kp = DoubleVar()
        ttk.Spinbox(fram_pid, textvariable=self.Kp, from_=-1000, to=1000, width=6, format="%.2f", increment=1.0).grid(row=0, column=1, pady=2)

        self.Ki = DoubleVar()
        ttk.Label(fram_pid, text="Ki :").grid(row=1, column=0, pady=2)
        ttk.Spinbox(fram_pid, textvariable=self.Ki, from_=-1000, to=1000, width=6, format="%.2f", increment=1.0).grid(row=1, column=1, pady=2)

        self.Kd = DoubleVar()
        ttk.Label(fram_pid, text="Kd :").grid(row=2, column=0, pady=2)
        ttk.Spinbox(fram_pid, textvariable=self.Kd, from_=-1000, to=1000, width=6, format="%.2f", increment=1.0).grid(row=2, column=1, pady=2)

        self.sample_time = DoubleVar()
        ttk.Label(fram_pid, text="sample time (Hz) :").grid(row=3, column=0, pady=2)
        ttk.Spinbox(fram_pid, textvariable=self.sample_time, from_=0, to=1000000, width=6, increment=1.0).grid(row=3, column=1, pady=2)


        self.filtre_derivee = DoubleVar()
        ttk.Label(fram_pid, text="filtre dérivée (Hz) :").grid(row=4, column=0, pady=2)
        ttk.Spinbox(fram_pid, textvariable=self.filtre_derivee, from_=0, to=1000000, width=6, increment=1.0).grid(row=4, column=1, pady=2)

        self.saturation = DoubleVar()
        ttk.Label(fram_pid, text="saturation :").grid(row=5, column=0, pady=2)
        ttk.Spinbox(fram_pid, textvariable=self.saturation, from_=0, to=100, width=6, increment=1.0).grid(row=5, column=1, pady=2)

        fram_pid.pack(side="top", pady=10)


        fram_bt = ttk.Frame(self)
        ttk.Button(fram_bt, text="cancel", command=lambda : self.close()).grid(row=0, column=0)
        ttk.Button(fram_bt, text="apply", command=lambda: self.sendPID()).grid(row=0, column=1)
        ttk.Button(fram_bt, text="send", command=lambda: (self.sendPID(), self.close())).grid(row=0, column=2)
        fram_bt.pack(side="bottom", pady=10, padx=10)

        self.list_data = [self.Kp, self.Ki, self.Kd, self.sample_time, self.filtre_derivee, self.saturation]

        try:
            self.Kp.set(self.parent.dico_config["Kp"+self.type])
            self.Ki.set(self.parent.dico_config["Ki"+self.type])
            self.Kd.set(self.parent.dico_config["Kd"+self.type])
            self.sample_time.set(self.parent.dico_config["sample_time"+self.type])
            self.filtre_derivee.set(self.parent.dico_config["filtre_derivee"+self.type])
            self.saturation.set(self.parent.dico_config["saturation" + self.type])
        except: pass

    def close(self):

        self.parent.dico_config["Kp"+self.type] = self.Kp.get()
        self.parent.dico_config["Ki"+self.type] = self.Ki.get()
        self.parent.dico_config["Kd"+self.type] = self.Kd.get()
        self.parent.dico_config["sample_time"+self.type] = self.sample_time.get()
        self.parent.dico_config["filtre_derivee"+self.type] = self.filtre_derivee.get()
        self.parent.dico_config["saturation" + self.type] = self.saturation.get()

        self.destroy()

    def sendPID(self):

        s = "PID_" + self.type + ":"

        for data in self.list_data:
            s += str(round(data.get(), 6)) + ";"

        self.parent.client.Send(s[:-1])

