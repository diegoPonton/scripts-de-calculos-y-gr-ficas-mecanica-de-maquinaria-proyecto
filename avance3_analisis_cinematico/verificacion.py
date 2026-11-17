"""
Verificaciones del análisis cinemático.

1. Cierre del lazo: la barra virtual mide L y theta4 = theta2 en todo el rango.
2. Sistema completo de velocidad: resolviendo las componentes x, y de
   v_B = v_A + w3 x r_B/A con w3 y w4 como incógnitas (sin usar la banda)
   se obtiene w3 = 0 y w4 = w2, salvo con el brazo vertical, donde el
   determinante se anula.
3. Derivación numérica: se deriva la posición de P y se compara con las
   expresiones analíticas de velocidad y aceleración.

Uso:  python verificacion.py
"""
import numpy as np

from parametros import L, D, T, THETA2_INICIAL, RECORRIDO
from cinematica import posicion, velocidad, estado, k_cruz, vector, MM_A_M


def cierre_del_lazo():
    th2 = np.linspace(THETA2_INICIAL, THETA2_INICIAL + RECORRIDO, 601)
    err_L = max(abs(posicion(t)["L4"] - L) for t in th2)
    err_th4 = max(abs(np.angle(np.exp(1j * (posicion(t)["theta4"] - t)))) for t in th2)
    return err_L, np.rad2deg(err_th4)


def sistema_completo_velocidad(theta2, omega2=1.0):
    """Resuelve [w3, w4] con las dos componentes de la ecuación de B (ec. 8 y 9)."""
    pos = posicion(theta2)
    r_A = pos["r_A"] * MM_A_M
    r_BA = vector(D, pos["theta3"]) * MM_A_M
    r_BO4 = vector(L, pos["theta4"]) * MM_A_M
    v_A = k_cruz(omega2, r_A)
    # w4 (k x r_B/O4) - w3 (k x r_B/A) = v_A
    M = np.column_stack([-k_cruz(1.0, r_BA), k_cruz(1.0, r_BO4)])
    det = np.linalg.det(M)
    if abs(det) < 1e-12:
        return None, det
    return np.linalg.solve(M, v_A), det


def derivacion_numerica(n=6001):
    tt = np.linspace(0, T, n)
    dt = tt[1] - tt[0]
    est = [estado(t) for t in tt]
    rP = np.array([s["r_P"] for s in est]) * MM_A_M
    vP = np.array([s["v_P"] for s in est])
    aP = np.array([s["a_P"] for s in est])
    vP_num = np.gradient(rP, dt, axis=0, edge_order=2)
    aP_num = np.gradient(vP_num, dt, axis=0, edge_order=2)
    k = slice(10, -10)
    err_v = np.max(np.linalg.norm(vP_num - vP, axis=1)[k])
    err_a = np.max(np.linalg.norm(aP_num - aP, axis=1)[k])
    w3 = max(abs(velocidad(s["theta2"], s["omega2"])["omega3"]) for s in est)
    return err_v, err_a, w3


def ejecutar():
    print("=" * 64)
    print("VERIFICACIONES")
    print("=" * 64)
    eL, eth = cierre_del_lazo()
    print(f"1. Cierre del lazo: error en |r4| = {eL:.1e} mm, error en theta4 - theta2 = {eth:.1e}°")

    print("\n2. Sistema completo de velocidad (omega2 = 1 rad/s, sin usar la banda):")
    print(f"   {'theta2':>7} {'det':>10} {'omega3':>9} {'omega4':>9}")
    for deg in (-60, 0, 35, 60, 89, 90, 91, 120, 180, 240):
        sol, det = sistema_completo_velocidad(np.deg2rad(deg))
        if sol is None:
            print(f"   {deg:>6}° {det:10.2e}   indeterminado (brazo vertical: lo resuelve la banda)")
        else:
            sol = np.round(sol, 4) + 0.0
            print(f"   {deg:>6}° {det:10.2e} {sol[0]:9.4f} {sol[1]:9.4f}")

    ev, ea, w3 = derivacion_numerica()
    print("\n3. Derivación numérica de la posición de P:")
    print(f"   error máximo en v_P = {ev:.1e} m/s, en a_P = {ea:.1e} m/s²")
    print(f"   |omega3| máximo en la maniobra = {w3:.1e} rad/s")
    return dict(err_v=ev, err_a=ea)


if __name__ == "__main__":
    ejecutar()
