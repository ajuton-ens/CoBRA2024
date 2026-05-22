from collections import deque
import threading
from tkinter import *
from tkinter import filedialog, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.gridspec import GridSpec
from matplotlib.patches import FancyArrowPatch
import time
from math import *

class Graphe():
    def __init__(self, root, frame, client):
        self.frame = frame
        self.root = root
        self.client = client

        self.fig = Figure(figsize=(8, 6))
        gs = GridSpec(2, 2, width_ratios=[2, 1])
        self.ax1 = self.fig.add_subplot(gs[0, 0])
        self.ax2 = self.fig.add_subplot(gs[1, 0])
        self.ax3 = self.fig.add_subplot(gs[:, 1])

        self.ax3.set_aspect('equal', adjustable='box')

        self.ax3.set_xlim(-1, 8)
        self.ax3.set_ylim(-1, 10)

        self.ax3.grid(True)


        self.arrow = FancyArrowPatch(
            (0, 0), (1, 1),
            arrowstyle='->',
            mutation_scale=20,
            linewidth=2
        )

        self.arrow_fix = FancyArrowPatch(
            (0, 0), (1, 1),
            arrowstyle='->',
            mutation_scale=20,
            linewidth=2,
            color='r'
        )




        self.running = True

        self.flux_resv_data = threading.Thread(target=self.run)

        n = 400
        self.x = deque(maxlen=n)
        self.y1 = deque(maxlen=n)
        self.y2 = deque(maxlen=n)
        self.y3 = deque(maxlen=n)

        self.dim_list = [self.x, self.y1, self.y2, self.y3]

        self.in_save = False
        self.gele = False

        self.line1, = self.ax1.plot([], label="grandeur")
        self.line2, = self.ax1.plot([], label="grandeur consigne")

        self.line3, = self.ax2.plot([], label="command moteur PID")

        self.ax1.grid(True)
        self.ax2.grid(True)

        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(fill=BOTH, expand=True)

        self.freq_update = 20

        self.update()

        self.buffer = ""

        self.donnee = {}

        self.grandeur = None





    def Start(self):
        self.flux_resv_data = threading.Thread(target=self.run)
        self.running = True
        self.flux_resv_data.start()
        self.ax3.add_patch(self.arrow)
        self.ax3.add_patch(self.arrow_fix)

    def Stop(self):
        self.running = False
        if self.arrow.axes is not None:
            self.arrow.remove()

        if self.arrow_fix.axes is not None:
            self.arrow_fix.remove()

    def run(self):
        while self.running:

            if not self.client.connected:   
                self.Stop()
                continue

            data = self.client.Resv()

            if not type(data) == str: continue
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

                data = trame.split(";")
                for d in data:
                    key, value = d.split(":")
                    self.donnee[key] = float(value)


            if not self.in_save and not self.gele:
                if self.grandeur == "altitude":
                    self.y1.append(self.donnee["alt"])
                    self.y2.append(self.donnee["alt_cons"])
                    self.y3.append(self.donnee["alt_force"])
                    self.x.append(self.donnee["t"])
                elif self.grandeur == "angle":
                    self.y1.append(self.donnee["angle"])
                    self.y2.append(self.donnee["angle_cons"])
                    self.y3.append(self.donnee["angle_force"])
                    self.x.append(self.donnee["t"])
                elif self.grandeur == "x":
                    self.y1.append(self.donnee["x"])
                    self.y2.append(0.0)
                    self.y3.append(0.0)
                    self.x.append(self.donnee["t"])
                elif self.grandeur == "y":
                    self.y1.append(self.donnee["y"])
                    self.y2.append(0.0)
                    self.y3.append(0.0)
                    self.x.append(self.donnee["t"])


                x = self.donnee["x"]
                y = self.donnee["y"]
                angle = self.donnee["angle"] * pi / 180

                g = 2

                self.arrow.set_positions((x, y), (x + cos(angle)*g, y + sin(angle)*g))

                x = self.donnee["x_fix"]
                y = self.donnee["x_fix"]
                angle = self.donnee["angle_fix"] * pi / 180

                self.arrow_fix.set_positions((x, y), (x + cos(angle) * g, y + sin(angle) * g))

    def update(self):

        self.line1.set_data(self.x, self.y1)
        self.line2.set_data(self.x, self.y2)
        self.ax1.relim()
        self.ax1.autoscale_view()

        self.line3.set_data(self.x, self.y3)
        self.ax2.relim()
        self.ax2.autoscale_view()

        self.canvas.draw()

        self.root.after(int(1000 / self.freq_update), self.update)

    def changeGrandeur(self, grandeur):
        self.grandeur = grandeur
        self.line1.set_label(self.grandeur)
        self.line2.set_label(self.grandeur + " consigne")
        self.ax1.legend(fontsize=8, frameon=False, loc='upper left')
        self.ax2.legend(fontsize=8, frameon=False, loc='upper left')
        self.canvas.draw_idle()

        self.clearGraph()


    def save_file(self):

        if not len(self.x): return

        self.in_save = True

        text = ""
        for i in range(len(self.x)):
            ligne = str(round(self.dim_list[0][i] - self.x[0], 6)).replace(".", ",")
            for k in range(1, len(self.dim_list)):
                ligne += ";" + str(self.dim_list[k][i]).replace(".", ",")
            text += ligne + "\n"
        self.in_save = False

        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Texte", "*.csv"), ("Tous les fichiers", "*.*")]
        )
        if not path:
            return

        try:
            with open(path, "w") as f:
                f.write(text)
        except:
            print("erreur d'enregistrement")


    def clearGraph(self):
        for dim in self.dim_list:
            dim.clear()