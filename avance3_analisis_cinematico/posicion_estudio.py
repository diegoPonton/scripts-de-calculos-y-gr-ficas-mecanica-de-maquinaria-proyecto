"""
Cálculo paso a paso en la posición de estudio theta2 = 35° (sección 5 del informe).

Uso:  python posicion_estudio.py
"""
import numpy as np

from parametros import THETA2_ESTUDIO, T, L
from cinematica import estado, tiempo_para


def calcular():
    t = tiempo_para(THETA2_ESTUDIO, 0.0, T / 2)   # el brazo pasa subiendo
    return estado(t)


def imprimir(s):
    th = s["theta2"]
    Lm = L / 1000
    print("=" * 64)
    print(f"POSICIÓN DE ESTUDIO  theta2 = {np.rad2deg(th):.1f}°")
    print("=" * 64)
    print(f"Instante de la maniobra       t       = {s['t']:.3f} s")
    print(f"Velocidad angular del brazo   omega2  = {s['omega2']:.3f} rad/s")
    print(f"Aceleración angular           alpha2  = {s['alpha2']:.3f} rad/s²")

    print("\n-- Posición --")
    print(f"theta3 = {np.rad2deg(s['theta3']):.1f}°    theta4 = {np.rad2deg(s['theta4']):.1f}°")
    print(f"r_A = 250 (cos35°, sen35°) = ({s['r_A'][0]:.1f}, {s['r_A'][1]:.1f}) mm")
    print(f"r_P = r_A + (e, 0)         = ({s['r_P'][0]:.1f}, {s['r_P'][1]:.1f}) mm")

    print("\n-- Velocidad --")
    print(f"v_A = ({Lm:.3f})({s['omega2']:.3f})(-sen35°, cos35°) "
          f"= ({s['v_A'][0]:.3f}, {s['v_A'][1]:.3f}) m/s")
    print(f"|v_P| = |v_A| = L*omega2 = {np.linalg.norm(s['v_P']):.3f} m/s")
    print(f"|v_G2| = {np.linalg.norm(s['v_G2']):.3f} m/s")
    print(f"omega3 = {s['omega3']:.3f} rad/s    omega4 = {s['omega4']:.3f} rad/s")

    print("\n-- Aceleración --")
    print(f"a_t = L*alpha2   = ({Lm:.3f})({s['alpha2']:.3f})   = {np.linalg.norm(s['a_t']):.3f} m/s²")
    print(f"a_n = L*omega2^2 = ({Lm:.3f})({s['omega2']:.3f})^2 = {np.linalg.norm(s['a_n']):.3f} m/s²")
    print(f"a_P = a_A = ({s['a_A'][0]:.3f}, {s['a_A'][1]:.3f}) m/s²")
    print(f"|a_P| = {np.linalg.norm(s['a_P']):.3f} m/s²    |a_G2| = {np.linalg.norm(s['a_G2']):.3f} m/s²")
    print(f"alpha3 = {s['alpha3']:.3f} rad/s²    alpha4 = {s['alpha4']:.3f} rad/s²")


if __name__ == "__main__":
    imprimir(calcular())
