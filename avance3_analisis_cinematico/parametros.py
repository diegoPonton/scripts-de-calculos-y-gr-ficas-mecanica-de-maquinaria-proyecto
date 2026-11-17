"""
Datos del mecanismo y de la maniobra de operación.

Mecanismo: brazo con gripper paralelo al suelo (cuatro barras virtual).
La correa, con poleas iguales, reemplaza a la barra superior del paralelogramo.

Eslabones:
    1  bancada: chasis y polea trasera fija
    2  brazo (manivela)
    3  polea delantera unida al gripper (acoplador)
    4  barra virtual: tramo de correa

Sistema de referencia: origen en el eje de la polea trasera (O2), x hacia
delante, y hacia arriba. Ángulos medidos desde +x en sentido antihorario.
"""
import numpy as np

# --- Geometría (plano del Avance 2) -----------------------------------------
L = 250.0            # distancia entre ejes de las poleas (brazo y correa) [mm]
R_TRASERA = 20.0     # radio de la polea trasera (Ø40 mm) [mm]
R_DELANTERA = 20.0   # radio de la polea delantera (Ø40 mm) [mm]
D = R_TRASERA        # bancada y acoplador del paralelogramo equivalente [mm]
E = 150.0            # eje delantero -> punta de los dedos (punto P) [mm]
THETA1 = np.deg2rad(90.0)   # orientación de la bancada O2 -> O4
THETA3_0 = np.deg2rad(90.0) # orientación inicial del acoplador

# --- Maniobra supuesta (el actuador se define en el Avance 4) ---------------
THETA2_INICIAL = np.deg2rad(-60.0)   # inicio del recorrido
RECORRIDO = np.deg2rad(300.0)        # rango de trabajo del brazo
T = 3.0                              # duración de la maniobra [s]

# --- Posición de estudio (vista lateral del Avance 2) -----------------------
THETA2_ESTUDIO = np.deg2rad(35.0)
