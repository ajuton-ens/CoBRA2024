# -*- coding: utf-8 -*-
"""
unidirectional airship speed simulation


"""

__author__ = "Bruno DENIS"

import typing
import math
import numpy
import pandas
import scipy.integrate
import matplotlib.pyplot as plt




def helice_str2tuple(chaine_helice: str) -> tuple:
    """Renvoie le couple (diamètre, pas) d'une hélice en inches."""
    diametre, pas = chaine_helice.lower().split("x")
    return (float(diametre), float(pas))


def test_helice_str2tuple():
    assert helice_str2tuple("6x5.5") == (6.0, 5.5)
    assert helice_str2tuple("6X5.5") == (6.0, 5.5)
    assert helice_str2tuple("10x8") == (10.0, 8.0)
    assert helice_str2tuple("12x10") == (12.0, 10.0)
    assert helice_str2tuple("4x3.5") == (4.0, 3.5)

test_helice_str2tuple()


def helice_tuple2str(diametre: float, pas: float) -> str:
    """Renvoie une chaine "{diamètre}x{pas}" d'une hélice."""
    return "x".join([
        convert_real_to_string(diametre),
        convert_real_to_string(pas),
    ])


def convert_real_to_string(number: float) -> str:
    """Converts real to string without unusefull tailing ".0"."""
    string = str(number)
    if "." in string:
        string = string .rstrip("0")
    return string.rstrip(".")


def test_convert_real_to_string():
    assert convert_real_to_string(10) == "10"
    assert convert_real_to_string(10.0) == "10"
    assert convert_real_to_string(10.5) == "10.5"
    assert convert_real_to_string(10.000) == "10"
    assert convert_real_to_string(10.) == "10"
    assert convert_real_to_string(-10.5) == "-10.5"
    assert convert_real_to_string(0) == "0"
    assert convert_real_to_string(0.5) == "0.5"
    assert convert_real_to_string(0.5000) == "0.5"

test_convert_real_to_string()

def test_helice_tuple2str():
    assert helice_tuple2str(6.0, 5.5) == "6x5.5"
    assert helice_tuple2str(10.0, 8.0) == "10x8"
    assert helice_tuple2str(12.0, 10.0) == "12x10"
    assert helice_tuple2str(4.0, 3.5) == "4x3.5"
    assert helice_tuple2str(0.0, 0.0) == "0x0"

test_helice_tuple2str()

def add_travel_times(distances, position_x, t, travel_time_table):
    """Append a row of travel times in travel_time_table.

    Parameters
    ----------
    distances : list of float
        Liste of distances to evaluate the travel time.
    position_x : numpy.ndarray
        1D array of positions along the x-axis.
    t : numpy.ndarray
        1D array of times.
    travel_time_table : list of list
        Table of travel times for different distances.
        
    Returns
    -------
    travel_time_table : list of list
        Table of travel times for different distances.
    """
    travel_time_row = list()  # empty row
    for distance in distances:
        indices = numpy.where(position_x >= distance)
        if len(indices[0]):  # if at least one index
            travel_time_row.append(t[indices[0][0]])
        else:
            travel_time_row.append("?")
    travel_time_table.append(travel_time_row)
    
    return travel_time_table


class Parameters_model_1(typing.NamedTuple):
    """Ensemble des paramètres du modèle v1."""

    l_dirigeable: float = 2.0
    r_dirigeable: float = 0.75
    vol_dirigeable: float = 3.0
    m_dirigeable: float = 3.0
    rho_air: float = 1.0
    c_x: float = 0.05
    omega_helice: float = None
    d_helice: float = None
    p_helice: float = None
    # alpha: float = 5.820e-06
    # beta: float = 3.100e-04

    def __repr__(self):
        """Renvoie une chaine exécutable qui pour recrée l'object."""
        return "{}(\n{})".format(
            type(self).__name__,
            "\n".join(["  " + s for s in self._str_param().split("\n")]),
        )

    def __str__(self):
        """Renvoie une chaine lisible qui liste les paramètres."""
        return "\n".join([self.basic_param_str(), self.deduced_param_str()])

    def basic_param_str(self) -> str:
        """Renvoie une description des paramètres de base."""
        return "\n".join(
            [
                "Paramètres de base du modèle",
                "----------------------------",
                self._basic_param_str()
            ]
        )

    def _basic_param_str(self) -> str:
        """Renvoie une chaine donnant la liste paramètres de base."""
        s = ""
        if self.l_dirigeable:
            s += f"l_dirigeable = {self.l_dirigeable:.2f},"
            s += "  # longueur de l'enveloppe ellipsoïde (m)\n"
        if self.r_dirigeable:
            s += f"r_dirigeable = {self.r_dirigeable:.2f},"
            s += "  # rayon de l'enveloppe ellipsoïde (m)\n"
        if self.vol_dirigeable:
            s += f"vol_dirigeable = {self.vol_dirigeable:.2f},"
            s += "  # volume de l'enveloppe (m³)\n"
        if self.m_dirigeable:
            s += f"m_dirigeable = {self.m_dirigeable:.2f},"
            s += "  # masse du dirigeable (kg)\n"
        if self.rho_air:
            s += f"rho_air = {self.rho_air:.2f},"
            s += "  # masse volumique de l'air (kg/m³)\n"
        if self.c_x:
            s += f"c_x = {self.c_x:.3f},"
            s += "  # coefficient aérodynamique de traînée (sans unité)\n"
        if self.omega_helice:
            s += f"omega_helice = {self.omega_helice:.1f},"
            s += "  # vitesse de rotation de l'hélice (rad/s)\n"
        if self.d_helice:
            s += f"d_helice = {self.d_helice:.2f},"
            s += "  # diamètre de l'hélice (in)\n"
        if self.p_helice:
            s += f"p_helice = {self.p_helice:.2f},"
            s += "  # pas (pitch) de l'hélice (in)\n"
        return s

    def deduced_param_str(self) -> str:
        """Renvoie une description des paramètres déduits."""
        return "\n".join(
            [
                "Paramètres déduits des paramètres de base",
                "-----------------------------------------",
                self._deduced_param_str()
            ]
        )

    def _deduced_param_str(self) -> str:
        """Renvoie une chaine donnant la liste paramètres déduits."""
        s = ""
        if self.s_reference:
            s += f"s_reference = {self.s_reference:.2f},"
            s += "  # surface de référence, paramètre déduit (m²)\n"
        if self.m_ajoutee:
            s += f"m_ajoutee = {self.m_ajoutee:.2f},"
            s += "  # masse ajoutée, paramètre déduit (kg)\n"
        if self.d_helice and self.p_helice:
            s += f"alpha = {self.alpha:.2e},"
            s += "  # coefficient du modèle de poussée, "
            s += "paramètre déduit (kg.m)\n"
        if self.d_helice and self.p_helice:
            s += f"beta = {self.beta:.2e},"
            s += "  # coefficient du modèle de poussée, "
            s += "paramètre déduit (kg)\n"
        return s

    @property
    def m_ajoutee(self):
        """Renvoie la masse inertielle ajoutée par l'air déplacé."""
        if (
                self.l_dirigeable and self.r_dirigeable
                and self.rho_air * self.vol_dirigeable
        ):
            e = (1 - ((self.r_dirigeable / 2) ** 2 /
                 (self.l_dirigeable / 2) ** 2)) ** 0.5
            alpha_0 = 2 * (1 - e**2) / e**3 * \
                (1 / 2 * numpy.log((1 + e) / (1 - e)) - e)
            m_air = self.rho_air * self.vol_dirigeable
            return m_air * alpha_0 / (2 - alpha_0)
        else:
            return None

    @property
    def s_reference(self):
        """Renvoie la surface de référence pour la traînée."""
        if self.r_dirigeable:
            return numpy.pi * self.r_dirigeable**2
        else:
            return None

    @property
    def alpha(self):
        """Renvoie le coefficient alpha du modèle de poussée."""
        if self.d_helice and self.p_helice:
            return 1.6956e-9 * self.d_helice**3.5 / self.p_helice**0.5
        else:
            return None

    @property
    def beta(self):
        """Renvoie le coefficient alpha du modèle de poussée."""
        if self.d_helice and self.p_helice:
            return 4.1944e-7 * self.d_helice**3.5 / self.p_helice**0.5
        else:
            return None

def model_speed_1(t, variables, parameters):
    """Renvoie les dérivées du temps pour vitesse et position du diregable."""
    vitesse_x, position_x, = variables  # décompacte la liste des variables
    p = parameters  # donne un nom court aux paramètres
    derivee_vitesse_x = (
        - 0.5 * p.rho_air * p.s_reference * p.c_x * vitesse_x**2
        - p.beta * p.omega_helice * vitesse_x
        + p.alpha * p.omega_helice**2
    ) / (p.m_dirigeable + p.m_ajoutee)
    derivee_position_x = vitesse_x
    return [derivee_vitesse_x, derivee_position_x]


def simul_model_1_influence_vitesse_helice(
    t_debut,
    t_fin,
    nb_point,
    model_speed_1,
    parameters,
    omega_helice_range,
    initiale_values=[0.0, 0.0],
    distances=[1, 2, 5, 10, 20],
):
    """
    Simulation du modèle v1.

    Paramètre variable: vitesse de rotation de l'hélice 

    Parameters
    ----------
    t_fin: float
        date initiale de la simulation (s)
    t_debut: float
        datesfinale de la simulation (s)
    nb_point: int
        nombre de date équidistante de simulation
    model_speed_1: function
        fonction qui donne la derivé de Vx en fonction du temps
    parameters: parameters_modele_v1
        valeur initiale des paramètres
    omega_helice_range: list
        liste des valeurs du paramètre omega_helice pour
        lesquelles on simule le modèle.
    initiale_values: list of float, optional
        valeurs initiales pour la vitesse et la position du dirigeable.
    distances: list of float
        Liste des distances pour lesquelles on évalue le temps de parcours.

    Returns
    -------
    report: str
        Rapport de simulation au format texte.
    fig: matplotlib.figure.Figure
        Courbe de simulation de la vitesse du dirigeable en fonction du temps.
    table: pandas.DataFrame
        Tableau des temps de parcours pour différentes distances.
    """
    t = numpy.linspace(t_debut, t_fin, nb_point)  # dates de simulation (s)
    # temps de de parcours pour différentes distances
    table_temps_de_parcours = list()

    report_title = "Simulation du modèle 1 pour une hélice {}".format(
            helice_tuple2str(parameters.d_helice, 
                             parameters.p_helice,
            )
        )
    report_title_underscore = "=" * len(report_title)
    report_subtitle = "Influence de la vitesse de rotation "
    report_subtitle += "de l'hélice $\Omega_{hélice}$"

    # --------------------------------------------
    # Création de la figure et collete des données
    # --------------------------------------------
    with plt.style.context("seaborn-v0_8-darkgrid"):
        
        fig, ax = plt.subplots()
        ax.set_title("\n".join([report_title, report_subtitle]))
        ax.set_xlabel("t (s)")
        ax.set_ylabel("Vx (m/s)")
    
        for omega_helice in omega_helice_range:
            
            # Résolution du système d'équations différentielles
            parameters = parameters._replace(omega_helice=omega_helice)
            sol = scipy.integrate.solve_ivp(
                model_speed_1,
                [t_debut, t_fin],
                initiale_values,
                method="RK45",
                args=[parameters],
                dense_output=True,
            )
            vitesse_x, position_x = sol.sol(t)  # mètre / seconde        

            # Tracé de la courbe
            label = "$\Omega_{hélice}$ = " + f"{omega_helice}" + " rad/s"
            ax.plot(t, vitesse_x, label=label)
            
            # Ajout d'un ligne dans le tableau des temps de parcours
            table_temps_de_parcours = add_travel_times(
                distances, 
                position_x, 
                t, 
                table_temps_de_parcours
            )

        ax.legend()

    # -----------------------------------------
    # Création du tableau des temps de parcours
    # -----------------------------------------
    
    table = pandas.DataFrame(
        table_temps_de_parcours,
        columns=pandas.Index([f"pour {p} m" for p in distances]),
        index=pandas.Index(omega_helice_range, name="Ω (rad/s)"),
    )
    table_title = "Tableau des temps de parcours en secondes"
    table.style.set_caption(table_title)
        
    report = "\n".join(
        [
            report_title,
            report_title_underscore,
            report_subtitle,
            "",
            str(parameters),
            table_title,
            "",
            table.to_markdown(),
            "",
        ]
    )
        
    return [report, fig, table]


def simul_model_1_influence_geometrie_helice(
    t_debut,
    t_fin,
    nb_point,
    model_speed_1,
    parameters,
    helice_range,
    initiale_values=[0.0, 0.0],
    distances=[1, 2, 5, 10, 20],
):
    """
    Simulation du modèle v1.

    Paramètre variable: géometrie de l'hélice , diamètre et pas

    Parameters
    ----------
    t_fin: float
        date initiale de la simulation (s)
    t_debut: float
        datesfinale de la simulation (s)
    nb_point: int
        nombre de date équidistante de simulation
    model_speed_1: function
        fonction qui donne la derivé de Vx en fonction du temps
    parameters: parameters_modele_v1
        valeur initiale des paramètres
    helice_range: list
        liste de chaine  de type "6x5.5" qui le presente le
        diamètre et pas d'une hélice.'
    initiale_values: list of float, optional
        valeurs initiales pour la vitesse et la position du dirigeable.
    distances: list of float
        Liste des distances pour lesquelles on évalue le temps de parcours.

    Returns
    -------
    report: str
        Rapport de simulation au format texte.
    fig: matplotlib.figure.Figure
        Courbe de simulation de la vitesse du dirigeable en fonction du temps.
    table: pandas.DataFrame
        Tableau des temps de parcours pour différentes distances.
    """
    t = numpy.linspace(t_debut, t_fin, nb_point)  # dates de simulation (s)
    # temps de de parcours pour différentes distances
    table_temps_de_parcours = list()  

    print("--->", parameters.omega_helice)
    report_title = " ".join(
        [
            "Simulation du modèle 1 pour une vitesse d'hélice $\Omega_{hélice}$",
            "= {:.0f} rad/s".format(parameters.omega_helice),
        ]
    )
    report_title_underscore = "=" * len(report_title)
    report_subtitle = "Influence de la géométrie de l'hélice (diamètre x pas)"

    # --------------------------------------------
    # Création de la figure et collete des données
    # --------------------------------------------
    with plt.style.context("seaborn-v0_8-darkgrid"):

        fig, ax = plt.subplots()
        ax.set_title("\n".join([report_title, report_subtitle]))
        ax.set_xlabel("t (s)")
        ax.set_ylabel("Vx (m/s)")
    
        for d_helice, p_helice in [helice_str2tuple(h) for h in helice_range]:

            # Résolution du système d'équations différentielles
            parameters = parameters._replace(
                d_helice=d_helice,
                p_helice=p_helice,
            )
            sol = scipy.integrate.solve_ivp(
                model_speed_1,
                [t_debut, t_fin],
                initiale_values,
                method="RK45",
                args=[parameters],
                dense_output=True,
            )
            vitesse_x, position_x = sol.sol(t)  # mètre / seconde
            
            # Tracé de la courbe
            label = "hélice {} in".format(helice_tuple2str(d_helice, p_helice))
            ax.plot(t, vitesse_x, label=label)
            
            # Ajout d'un ligne dans le tableau des temps de parcours
            table_temps_de_parcours = add_travel_times(
                distances, 
                position_x, 
                t, 
                table_temps_de_parcours
            )

        ax.legend()

    # -----------------------------------------
    # Création du tableau des temps de parcours
    # -----------------------------------------
    
    table = pandas.DataFrame(
        table_temps_de_parcours,
        columns=pandas.Index([f"pour {p} m" for p in distances]),
        index=pandas.Index(helice_range, name="Hélice"),
    )
    table_title = "Tableau des temps de parcours en secondes"
    table.style.set_caption(table_title)
        
    report = "\n".join(
        [
            report_title,
            report_title_underscore,
            report_subtitle,
            "",
            str(parameters),
            table_title,
            "",
            table.to_markdown(),
            "",
        ]
    )

    return [report, fig, table]
            

def simul_model_1_influence_masse_dirigeable(
    t_debut,
    t_fin,
    nb_point,
    model_speed_1,
    parameters,
    masse_dirigeable_range,
    initiale_values=[0.0, 0.0],
    distances=[1, 2, 5, 10, 20],
):
    """
    Simulation du modèle v1.

    Paramètre variable: masse du dirigeable 

    Parameters
    ----------
    t_fin: float
        date initiale de la simulation (s)
    t_debut: float
        datesfinale de la simulation (s)
    nb_point: int
        nombre de date équidistante de simulation
    model_speed_1: function
        fonction qui donne la derivé de Vx en fonction du temps
    parameters: parameters_modele_v1
        valeur initiale des paramètres
    masse_dirigeable_range: list
        liste des valeurs du paramètre m_dirigeable pour
        lesquelles on simule le modèle
    initiale_values: list of float, optional
        valeurs initiales pour la vitesse et la position du dirigeable.
    distances: list of float
        Liste des distances pour lesquelles on évalue le temps de parcours.

    Returns
    -------
    report: str
        Rapport de simulation au format texte.
    fig: matplotlib.figure.Figure
        Courbe de simulation de la vitesse du dirigeable en fonction du temps.
    table: pandas.DataFrame
        Tableau des temps de parcours pour différentes distances.
    """
    t = numpy.linspace(t_debut, t_fin, nb_point)  # dates de simulation (s)
    # temps de de parcours pour différentes distances
    table_temps_de_parcours = list()

    report_title = " ".join(
        [
            "Simulation du modèle 1 pour une hélice {}".format(
                helice_tuple2str(
                    parameters.d_helice, 
                    parameters.p_helice,
                )
            ),
            "à $\Omega_{hélice}$ =",
            "{:.0f} rad/s\n".format(parameters.omega_helice),
        ]
    )    
    report_title_underscore = "=" * len(report_title)
    report_subtitle = "Influence de la masse du "
    report_subtitle += "dirigeabme $m_{dirigeable}$"

    # --------------------------------------------
    # Création de la figure et collete des données
    # --------------------------------------------
    with plt.style.context("seaborn-v0_8-darkgrid"):
        
        fig, ax = plt.subplots()
        ax.set_title("\n".join([report_title, report_subtitle]))
        ax.set_xlabel("t (s)")
        ax.set_ylabel("Vx (m/s)")
    
        for masse_dirigeable in masse_dirigeable_range:

            # Résolution du système d'équations différentielles
            parameters = parameters._replace(
                m_dirigeable=masse_dirigeable
            )
            sol = scipy.integrate.solve_ivp(
                model_speed_1,
                [t_debut, t_fin],
                initiale_values,
                method="RK45",
                args=[parameters],
                dense_output=True,
            )
            vitesse_x, position_x = sol.sol(t)  # mètre / seconde

            # Tracé de la courbe
            label = "$m_{dirigeable}$ = " + f"{masse_dirigeable}" + " kg"
            ax.plot(t, vitesse_x, label=label)
            
            # Ajout d'un ligne dans le tableau des temps de parcours
            table_temps_de_parcours = add_travel_times(
                distances, 
                position_x, 
                t, 
                table_temps_de_parcours
            )
        
        plt.legend()
    
    # -----------------------------------------
    # Création du tableau des temps de parcours
    # -----------------------------------------
    
    table = pandas.DataFrame(
        table_temps_de_parcours,
        columns=pandas.Index([f"pour {p} m" for p in distances]),
        index=pandas.Index(masse_dirigeable_range, name="masse (kg)"),
    )
    table_title = "Tableau des temps de parcours en secondes"
    table.style.set_caption(table_title)
        
    report = "\n".join(
        [
            report_title,
            report_title_underscore,
            report_subtitle,
            "",
            str(parameters),
            table_title,
            "",
            table.to_markdown(),
            "",
        ]
    )
        
    return [report, fig, table]

class Parameters_model_2(typing.NamedTuple):
    """Ensemble des paramètres du modèle v2."""
    
    l_dirigeable: float = 2.0
    r_dirigeable: float = 0.75
    vol_dirigeable: float = 3.0
    m_dirigeable: float = 3.0
    rho_air: float = 1.0
    c_x: float = 0.05
    d_helice: float = None
    p_helice: float = None

    eta: float = 0.75
    j_helice: float = 3e-6  # kg.m²
    j_moteur: float = 2e-6  # kg.m²
    f: float = 1e-3  # N.m/(rad/s)
    k_m: float = 1530  # rpm/V
    r_m: float = 0.25  # Ω
    l_m: float = 0.1e-3  # H
    u_moteur: float = 6.0  # V
    i_saturation: float = 2.0  # A
    u_alim: float = 14.4  # V
    u_consigne: float = 14.4  # V
    t_montee: float = 0.3  # s
    
    u_0: float = None  # V


    def parameters_model_1(
        self,
        l_dirigeable,  # longueur de l'enveloppe ellipsoïde (m)
        r_dirigeable,  # rayon de l'enveloppe ellipsoïde (m)
        vol_dirigeable,  # volume de l'enveloppe (m³)
        m_dirigeable,  # masse du dirigeable (kg)
        rho_air,  # masse volumique de l'air (kg/m³)
        c_x,  # coefficient aérodynamique de traînée (sans unité)
        d_helice,  # diamètre de l'hélice (in)
        p_helice,  # pas (pitch) de l'hélice (in)
    ):
        return Parameters_model_1(
            l_dirigeable=l_dirigeable,  
            r_dirigeable=r_dirigeable,  
            vol_dirigeable=vol_dirigeable,
            m_dirigeable=m_dirigeable,  
            rho_air=rho_air, 
            c_x=c_x, 
            d_helice=d_helice,
            p_helice=p_helice,
        )

    def __str__(self):
        """Renvoie une chaine lisible qui liste les paramètres."""
        return "\n".join([self.basic_param_str(), self.deduced_param_str()])

    def basic_param_str(self) -> str:
        """Renvoie une description des paramètres de base."""
        return "\n".join(
            [
                "Paramètres de base du modèle",
                "----------------------------",
                self._basic_param_str()
            ]
        )
        
    def _basic_param_str(self) -> str:
        """Renvoie une chaine donnant la liste paramètres de base."""
        s = self.parameters_model_1(
            self.l_dirigeable,  # longueur de l'enveloppe ellipsoïde (m)
            self.r_dirigeable,  # rayon de l'enveloppe ellipsoïde (m)
            self.vol_dirigeable,  # volume de l'enveloppe (m³)
            self.m_dirigeable,  # masse du dirigeable (kg)
            self.rho_air,  # masse volumique de l'air (kg/m³)
            self.c_x,  # coefficient aérodynamique de traînée (sans unité)
            self.d_helice,  # diamètre de l'hélice (in)
            self.p_helice,  # pas (pitch) de l'hélice (in)
        )._basic_param_str()
        if self.eta:
            s += f"eta = {self.eta:.2f}"
            s += "  # rendement de l'hélice (sans unité)\n"
        if self.j_helice:
            s += f"j_helice = {self.j_helice:.2e}"
            s += "  # moment d'inertie de l'hélice (kg.m²)\n"
        if self.j_moteur:
            s += f"j_moteur = {self.j_moteur:.2e}"
            s += "  # moment d'inertie du rotor du moteur (kg.m²)\n"
        if self.f:
            s += f"f = {self.f:.2e}"
            s += "  # frottement au niveau du moteur (N.m/(rad/s))\n"
        if self.k_m:
            s += f"k_m = {self.k_m}"
            s += "  # constante moteur (rpm/s)\n"
        if self.r_m:
            s += f"r_m = {self.r_m}"
            s += "  # résistance du moteur (Ω)\n"
        if self.l_m:
            s += f"l_m = {self.l_m:.2e}"
            s += "  # inductance du moteur (H)\n"
        if self.u_moteur:
            s += f"u_moteur = {self.u_moteur:.2f}"
            s += "  # tension appliquée au moteur (V)\n"
        if self.u_alim:
            s += f"u_alim = {self.u_alim:.1f}"
            s += "  # tension l'alimentation de l'ESC (V)\n"
        if self.u_consigne:
            s += f"u_consigne = {self.u_consigne:.1f}"
            s += "  # est la tension visée pour le moteur (V)\n"
        if self.u_moteur:
            s += f"t_montee = {self.t_montee:.3f}"
            s += "  # durée de montée de la rampe de vitesse ESC (s)\n"
        return s

    def deduced_param_str(self) -> str:
        """Renvoie une description des paramètres déduits."""
        return "\n".join(
            [
                "Paramètres déduits des paramètres de base",
                "-----------------------------------------",
                self._deduced_param_str()
            ]
        )

    def _deduced_param_str(self) -> str:
        """Renvoie une chaine donnant la liste paramètres déduits."""
        s = self.parameters_model_1(
            self.l_dirigeable,  # longueur de l'enveloppe ellipsoïde (m)
            self.r_dirigeable,  # rayon de l'enveloppe ellipsoïde (m)
            self.vol_dirigeable,  # volume de l'enveloppe (m³)
            self.m_dirigeable,  # masse du dirigeable (kg)
            self.rho_air,  # masse volumique de l'air (kg/m³)
            self.c_x,  # coefficient aérodynamique de traînée (sans unité)
            self.d_helice,  # diamètre de l'hélice (in)
            self.p_helice,  # pas (pitch) de l'hélice (in)
        )._deduced_param_str()
        if self.k_e:
            s += f"k_e = {self.k_e:.2e},"
            s += "  # constant de f.e.m. du moteur (V.s.rad⁻¹)\n"
        if self.k_c:
            s += f"k_c = {self.k_c:.2e},"
            s += "  # constante de couple du moteur (A.N⁻¹.m⁻¹)\n"
        return s

    @property
    def m_ajoutee(self):
        """Renvoie la masse inertielle ajoutée par l'air déplacé."""
        if (
                self.l_dirigeable and self.r_dirigeable
                and self.rho_air * self.vol_dirigeable
        ):
            e = (1 - ((self.r_dirigeable / 2) ** 2 /
                 (self.l_dirigeable / 2) ** 2)) ** 0.5
            alpha_0 = 2 * (1 - e**2) / e**3 * \
                (1 / 2 * numpy.log((1 + e) / (1 - e)) - e)
            m_air = self.rho_air * self.vol_dirigeable
            return m_air * alpha_0 / (2 - alpha_0)
        else:
            return None

    @property
    def s_reference(self):
        """Renvoie la surface de référence pour la traînée."""
        if self.r_dirigeable:
            return numpy.pi * self.r_dirigeable**2
        else:
            return None

    @property
    def alpha(self):
        """Renvoie le coefficient alpha du modèle de poussée."""
        if self.d_helice and self.p_helice:
            return 1.6956e-9 * self.d_helice**3.5 / self.p_helice**0.5
        else:
            return None

    @property
    def beta(self):
        """Renvoie le coefficient alpha du modèle de poussée."""
        if self.d_helice and self.p_helice:
            return 4.1944e-7 * self.d_helice**3.5 / self.p_helice**0.5
        else:
            return None


    @property
    def k_e(self):
        """Renvoie la constante de fem du moteur (V.s.rad⁻¹)."""
        if self.k_m:
            return 1 / (self.k_m * scipy.pi / 30)
        else:
            return None

    @property
    def k_c(self):
        """Renvoie la constante de couple du moteur (A.N⁻¹.m⁻¹)."""
        return self.k_e


def model_speed_2(t, variables, parameters):
    """Renvoie le vecteur des dérivées par rapport au temps."""
    vitesse_x, position_x, omega_helice, i_moteur, = variables
    p = parameters  # donne un nom court aux paramètres
    
    # Calcul de la tension moteur
    t_limite = p.t_montee * abs((p.u_consigne - p.u_0)/p.u_alim)
    if t <= 0:
        u_moteur = p.u_0
    elif t < t_limite:
        u_moteur = (
            p.u_0 
            + math.copysign(1, p.u_consigne - p.u_0) * p.u_alim * t / p.t_montee
        )
    else:
        u_moteur = p.u_consigne
        
    # Calcul des dérivées
    derivee_vitesse_x = (
        - 0.5 * p.rho_air * p.s_reference * p.c_x * vitesse_x**2
        - p.beta * omega_helice * vitesse_x
        + p.alpha * omega_helice**2
    ) / (p.m_dirigeable + p.m_ajoutee)
    derivee_position_x = vitesse_x
    derivee_omega_helice = (
        p.eta * p.k_c * i_moteur
        - p.alpha * vitesse_x * omega_helice
        + p.beta * vitesse_x**2
    ) / (p.eta * (p.j_moteur + p.j_helice))
    derivee_i_moteur = (
        u_moteur - p.r_m * i_moteur - p.k_e * omega_helice
    ) / p.l_m
    # if (i_moteur >= p.i_saturation) and (derivee_i_moteur > 0):
    #     derivee_i_moteur = 0
    return [
        derivee_vitesse_x,
        derivee_position_x,
        derivee_omega_helice,
        derivee_i_moteur,
    ]


def simul_model_2_simulation(
        t_debut,
        t_fin,
        nb_point,
        model_speed_2,
        parameters,
        initiale_values=[0.0, 0.0, 0.0, 0.0], # Vx, Px, Ω, Imot initiales
):
    """
    Simulation du modèle v2.

    Paramètre variable: ...

    Parameters
    ----------

    Returns
    -------
    None.

    """

    t = numpy.linspace(t_debut, t_fin, nb_point)  # dates de simulation (s)
    
    u_0 = initiale_values[2] / parameters.k_m
    parameters = parameters._replace(u_0=u_0)

    report_title = "Simulation du modèle 2"
    report_title_underscore = "=" * len(report_title)
    report_subtitle = "Estimation du courant moteur $I_{moteur}$"


    # --------------------------------------------
    # Création de la figure et collete des données
    # --------------------------------------------
    with plt.style.context("seaborn-v0_8-darkgrid"):
        
        fig, axs = plt.subplots(3)
        fig.suptitle("\n".join([report_title, report_subtitle]))
        axs[0].set_xlabel("t (s)")
        axs[0].set_ylabel("Vx (m/s)")
        axs[1].set_xlabel("t (s)")
        axs[1].set_ylabel("Ω (rad/s)")
        axs[2].set_xlabel("t (s)")
        axs[2].set_ylabel("I (A)")

        # Résolution du système d'équations différentielles
        sol = scipy.integrate.solve_ivp(
            model_speed_2,
            [t_debut, t_fin],
            initiale_values,
            method="RK45",
            args=[parameters],
            dense_output=True,
        )
        vitesse_x, position_x, omega_helice, i_moteur, = sol.sol(t)

        # Tracé des courbes
        label = "Vitesse linéaire du dirigeable"
        axs[0].plot(t, vitesse_x, "blue", label=label)
        label = "Vitesse de rotation de l'hélice"
        axs[1].plot(t, omega_helice, "orange", label=label)
        label = "Courant moteur"
        axs[2].plot(t, i_moteur, "green", label=label)

        plt.legend()
        
    # -----------------------------------------
    # Création du tableau des temps de parcours
    # -----------------------------------------
    
    report = "\n".join(
        [
            report_title,
            report_title_underscore,
            report_subtitle,
            "",
            str(parameters),
        ]
    )
        
    return [report, fig]


def main():
    
    # Simulation du modèle 1
    # ----------------------
    # Etude de l'influence de la vitesse de rotation de l'hélice

    parameters = Parameters_model_1(
        l_dirigeable=2.0,  # longueur de l'enveloppe ellipsoïde (m)
        r_dirigeable=0.75,  # rayon de l'enveloppe ellipsoïde (m)
        vol_dirigeable=3.0,  # volume de l'enveloppe (m³)
        m_dirigeable=3.0,  # masse du dirigeable (kg)
        rho_air=1.0,  # masse volumique de l'air (kg/m³)
        c_x=0.05,  # coefficient aérodynamique de traînée (sans unité)
        d_helice=6.0,  # diamètre de l'hélice (in)
        p_helice=4.0,  # pas (pitch) de l'hélice (in)
    )

    report, fig, table = simul_model_1_influence_vitesse_helice(
        0.0,  # date initiale de la simulation (s)
        120.0,  # date finale de la simulation (s)
        1000,  # nombre de dates de simulation
        model_speed_1,  # fonction qui donne les derivées de Vx et Px
        parameters,  # valeurs des paramètres
        [200, 400, 600, 800],  # valeurs du paramètre omega_helice (rad/s)
        initiale_values=[
            0.0, 0.0
        ],  # vitesse (m/s) et position (m) initiales
    )
    
    print(report)

    # Simulation du modèle 1
    # ----------------------
    # Etude de l'influence de la géométrie de l'hélice 
    # (son diamètre et son pas)

    parameters = Parameters_model_1(
        l_dirigeable=2.0,  # longueur de l'enveloppe ellipsoïde (m)
        r_dirigeable=0.75,  # rayon de l'enveloppe ellipsoïde (m)
        vol_dirigeable=3.0,  # volume de l'enveloppe (m³)
        m_dirigeable=3.0,  # masse du dirigeable (kg)
        rho_air=1.0,  # masse volumique de l'air (kg/m³)
        c_x=0.05,  # coefficient aérodynamique de traînée (sans unité)
        omega_helice=600.0,  # vitesse de rotation de l'hélice (rad/s)
    )

    report, fig, table = simul_model_1_influence_geometrie_helice(
        0.0,  # date initiale de la simulation (s)
        120.0,  # date finale de la simulation (s)
        1000,  # nombre de dates de simulation
        model_speed_1,  # fonction qui donne les derivées de Vx et Px
        parameters,  # valeurs des paramètres
        [
            "5.1x4.5",
            "6x4",
            "6x5.5",
            "7x4",
            "7x5",
            "7x6",
        ],  # valeurs diamètre x pas des helices (in)
        initiale_values=[
            0.0, 0.0
        ],  # vitesse (m/s) et position (m) initiales
    )
    
    print(report)

    # Simulation du modèle 1
    # ----------------------
    # Etude de l'influence de la masse du dirigeable

    parameters = Parameters_model_1(
        l_dirigeable=2.0,  # longueur de l'enveloppe ellipsoïde (m)
        r_dirigeable=0.75,  # rayon de l'enveloppe ellipsoïde (m)
        vol_dirigeable=3.0,  # volume de l'enveloppe (m³)
        rho_air=1.0,  # masse volumique de l'air (kg/m³)
        c_x=0.05,  # coefficient aérodynamique de traînée (sans unité)
        omega_helice=600.0,  # vitesse de rotation de l'hélice (rad/s)
        d_helice=6.0,  # diamètre de l'hélice (in)
        p_helice=4.0,  # pas (pitch) de l'hélice (in)
    )

    report, fig, table = simul_model_1_influence_masse_dirigeable(
        0.0,  # date initiale de la simulation (s)
        120.0,  # date finale de la simulation (s)
        1000,  # nombre de dates de simulation
        model_speed_1,  # fonction qui donne la derivé de Vx
        parameters,  # valeurs des paramètres
        [2.5, 3.0, 3.5, 4.0],  # masse du dirigeable (kg)
        initiale_values=[
            0.0, 0.0
        ],  # vitesse (m/s) et position (m) initiales
    )

    print(report)
    
    # Simulation du modèle 2
    # ----------------------
    #

    parameters = Parameters_model_2(
        l_dirigeable=2.0,  # longueur de l'enveloppe ellipsoïde (m)
        r_dirigeable=0.75,  # rayon de l'enveloppe ellipsoïde (m)
        vol_dirigeable=3.0,  # volume de l'enveloppe (m³)
        m_dirigeable=3.0,  # masse du dirigeable (kg)
        rho_air=1.0,  # masse volumique de l'air (kg/m³)
        c_x=0.05,  # coefficient aérodynamique de traînée (sans unité)
        d_helice=6.0,  # diamètre de l'hélice (in)
        p_helice=4.0,  # pas (pitch) de l'hélice (in)
        eta=0.75,  # rendement de l'hélice (sans unité)
        j_helice=3e-6,  # moment d'inertie de l'hélice (kg.m²)
        j_moteur=2e-6,  # moment d'inertie du rotor du moteur (kg.m²)
        f=1e-3,  # frottement au niveau du moteur (N.m/(rad/s))
        k_m=1530,  # constante moteur (rpm/s)
        r_m=0.25,  # résistance du moteur (Ω)
        l_m=0.1e-3,  # inductance du moteur (H)
        u_alim=14.4,  # tension l'alimentation de l'ESC (V)
        t_montee=0.5,  # durée de montée de la rampe de vitesse ESC (s)
    )

    report, fig = simul_model_2_simulation(
        0.0,  # date initiale de la simulation (s)
        1.0,  # date finale de la simulation (s)
        100,  # nombre de dates de simulation
        model_speed_2,  # fonction qui donne la derivé de Vx
        parameters,  # valeurs des paramètres
        initiale_values=[0.0, 0.0, 0.0, 0.0],  # Vx, Px, Ω, Imot initiales
    )

    print(report)

if __name__ == "__main__":
    main()
