"""
Análisis cinemático del brazo con gripper paralelo al suelo.

Cada función sigue el método vectorial del curso (sistemas de coordenadas
fijas y móviles) y las ecuaciones del informe del Avance 3:

    posición     ec. (1)-(5)    lazo vectorial + relación de la banda
    velocidad    ec. (6)-(10)   v_B = v_A + w x r_B/A
    aceleración  ec. (11)-(14)  a_B = a_A + alpha x r_B/A - w^2 r_B/A
    maniobra     ec. (15)       ley cicloidal

Unidades: longitudes en mm, ángulos en rad, velocidades en m/s y
aceleraciones en m/s^2.
"""
import numpy as np

from parametros import (L, D, E, R_TRASERA, R_DELANTERA, THETA1, THETA3_0,
                        THETA2_INICIAL, RECORRIDO, T)

MM_A_M = 1e-3
RELACION_BANDA = R_TRASERA / R_DELANTERA   # r1 / r3


def k_cruz(w, r):
    """Producto cruz (w k) x r para un vector r = (x, y) en el plano."""
    return w * np.array([-r[1], r[0]])


def vector(magnitud, angulo):
    return magnitud * np.array([np.cos(angulo), np.sin(angulo)])


# --------------------------------------------------------------------------
# Ley de movimiento del brazo (ec. 15)
# --------------------------------------------------------------------------
def ley_cicloidal(t):
    """theta2, omega2 y alpha2 del brazo en el instante t [s]."""
    tau = t / T
    theta2 = THETA2_INICIAL + RECORRIDO * (tau - np.sin(2 * np.pi * tau) / (2 * np.pi))
    omega2 = RECORRIDO / T * (1 - np.cos(2 * np.pi * tau))
    alpha2 = 2 * np.pi * RECORRIDO / T**2 * np.sin(2 * np.pi * tau)
    return theta2, omega2, alpha2


# --------------------------------------------------------------------------
# Posición (ec. 1-5)
# --------------------------------------------------------------------------
def posicion(theta2):
    """Ángulos de los eslabones y posición de los puntos para un theta2."""
    # Relación de la banda con el brazo como referencia (ec. 3):
    # (w3 - w2)/(w1 - w2) = r1/r3, con w1 = 0  ->  w3 = w2 (1 - r1/r3)
    # Integrando: theta3 = theta3_0 + (1 - r1/r3)(theta2 - theta2_0)
    theta3 = THETA3_0 + (1 - RELACION_BANDA) * (theta2 - THETA2_INICIAL)

    # Lazo vectorial r2 + r3 = r1 + r4 (ec. 1)  ->  r4 = r2 + r3 - r1
    r2 = vector(L, theta2)
    r3 = vector(D, theta3)
    r1 = vector(D, THETA1)
    r4 = r2 + r3 - r1
    theta4 = np.arctan2(r4[1], r4[0])

    r_A = r2                         # centro de la polea delantera
    r_B = r2 + r3                    # punto del acoplador a distancia d de A
    r_P = r_A + np.array([E, 0.0])   # punta de los dedos (gripper horizontal)
    r_G2 = r_A / 2                   # centro de masa del brazo
    return dict(theta3=theta3, theta4=theta4, L4=np.hypot(*r4),
                r_A=r_A, r_B=r_B, r_P=r_P, r_G2=r_G2)


# --------------------------------------------------------------------------
# Velocidad (ec. 6-10)
# --------------------------------------------------------------------------
def velocidad(theta2, omega2):
    pos = posicion(theta2)
    th3, th4 = pos["theta3"], pos["theta4"]
    r_A = pos["r_A"] * MM_A_M
    r_BA = vector(D, th3) * MM_A_M      # r_B/A
    r_BO4 = vector(L, th4) * MM_A_M     # r_B/O4

    # Punto A del brazo (ec. 6)
    v_A = k_cruz(omega2, r_A)

    # Banda (derivada de la ec. 3)
    omega3 = omega2 * (1 - RELACION_BANDA)

    # Punto B desde la barra 4 y desde el acoplador (ec. 7):
    #   w4 k x r_B/O4 = v_A + w3 k x r_B/A
    # Componentes x, y (ec. 8 y 9). Única incógnita: w4. Se resuelve por
    # mínimos cuadrados con ambas componentes, así no hay división entre cero
    # cuando el brazo está vertical.
    a = k_cruz(1.0, r_BO4)
    b = v_A + k_cruz(omega3, r_BA)
    omega4 = a.dot(b) / a.dot(a)

    # Puntos del gripper y del brazo (ec. 10)
    v_P = v_A + k_cruz(omega3, (pos["r_P"] - pos["r_A"]) * MM_A_M)
    v_B = v_A + k_cruz(omega3, r_BA)
    v_G2 = k_cruz(omega2, pos["r_G2"] * MM_A_M)
    return dict(pos, omega3=omega3, omega4=omega4,
                v_A=v_A, v_B=v_B, v_P=v_P, v_G2=v_G2)


# --------------------------------------------------------------------------
# Aceleración (ec. 11-14)
# --------------------------------------------------------------------------
def aceleracion(theta2, omega2, alpha2):
    vel = velocidad(theta2, omega2)
    th3, th4 = vel["theta3"], vel["theta4"]
    w3, w4 = vel["omega3"], vel["omega4"]
    r_A = vel["r_A"] * MM_A_M
    r_BA = vector(D, th3) * MM_A_M
    r_BO4 = vector(L, th4) * MM_A_M
    r_PA = (vel["r_P"] - vel["r_A"]) * MM_A_M

    # Punto A: tangencial + normal (ec. 11). Sin Coriolis: no hay deslizamiento.
    a_t = k_cruz(alpha2, r_A)
    a_n = -omega2**2 * r_A
    a_A = a_t + a_n

    # Banda (segunda derivada de la ec. 3)
    alpha3 = alpha2 * (1 - RELACION_BANDA)

    # Punto B desde la barra 4 y desde el acoplador (ec. 12 y 13):
    #   alpha4 k x r_B/O4 - w4^2 r_B/O4 = a_A + alpha3 k x r_B/A - w3^2 r_B/A
    a = k_cruz(1.0, r_BO4)
    b = a_A + k_cruz(alpha3, r_BA) - w3**2 * r_BA + w4**2 * r_BO4
    alpha4 = a.dot(b) / a.dot(a)

    # Puntos del gripper y del brazo (ec. 14)
    a_P = a_A + k_cruz(alpha3, r_PA) - w3**2 * r_PA
    a_G2 = a_A / 2
    return dict(vel, alpha3=alpha3, alpha4=alpha4,
                a_A=a_A, a_t=a_t, a_n=a_n, a_P=a_P, a_G2=a_G2)


def estado(t):
    """Estado cinemático completo en el instante t de la maniobra."""
    theta2, omega2, alpha2 = ley_cicloidal(t)
    s = aceleracion(theta2, omega2, alpha2)
    s.update(t=t, theta2=theta2, omega2=omega2, alpha2=alpha2)
    return s


def tiempo_para(theta2, t_min=0.0, t_max=T):
    """Instante de la maniobra en que el brazo pasa por theta2 (bisección)."""
    lo, hi = t_min, t_max
    for _ in range(100):
        mid = (lo + hi) / 2
        if ley_cicloidal(mid)[0] < theta2:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2
