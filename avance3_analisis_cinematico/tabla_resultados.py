"""
Resultados cada 30° durante la maniobra (Tabla 2 del informe) y valores máximos.

Genera:
    resultados/tabla_resultados.csv
    resultados/tabla_resultados.tex   (filas para la tabla del informe)

Uso:  python tabla_resultados.py
"""
import csv
import os

import numpy as np

from parametros import T
from cinematica import estado, tiempo_para

CARPETA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultados")
COLUMNAS = ["theta2_deg", "t_s", "xP_mm", "yP_mm", "omega2_rad_s",
            "alpha2_rad_s2", "vP_m_s", "aP_m_s2"]


def filas(paso_deg=30):
    out = []
    for deg in range(-60, 241, paso_deg):
        if deg == -60:
            t = 0.0
        elif deg == 240:
            t = T
        else:
            t = tiempo_para(np.deg2rad(deg))
        s = estado(t)
        out.append([deg, t, s["r_P"][0], s["r_P"][1], s["omega2"], s["alpha2"],
                    np.linalg.norm(s["v_P"]), np.linalg.norm(s["a_P"])])
    return out


def maximos(n=6001):
    tt = np.linspace(0, T, n)
    est = [estado(t) for t in tt]
    vP = np.array([np.linalg.norm(s["v_P"]) for s in est])
    aP = np.array([np.linalg.norm(s["a_P"]) for s in est])
    w2 = np.array([s["omega2"] for s in est])
    a2 = np.array([s["alpha2"] for s in est])
    iv, ia = int(np.argmax(vP)), int(np.argmax(aP))
    return dict(
        omega2=w2.max(), alpha2=np.abs(a2).max(),
        vP=vP[iv], theta2_vP=np.rad2deg(est[iv]["theta2"]), t_vP=tt[iv],
        aP=aP[ia], theta2_aP=np.rad2deg(est[ia]["theta2"]), t_aP=tt[ia],
    )


def _limpio(x, dec):
    x = 0.0 if abs(x) < 0.5 * 10**-dec else x
    return f"{x:.{dec}f}"


def guardar(tabla):
    os.makedirs(CARPETA, exist_ok=True)
    with open(os.path.join(CARPETA, "tabla_resultados.csv"), "w", newline="", encoding="utf8") as fh:
        w = csv.writer(fh)
        w.writerow(COLUMNAS)
        for f in tabla:
            w.writerow([f[0]] + [round(v, 4) for v in f[1:]])
    decs = [3, 1, 1, 3, 3, 3, 3]
    lineas = []
    for f in tabla:
        celdas = [str(f[0])] + [_limpio(v, d) for v, d in zip(f[1:], decs)]
        lineas.append(" & ".join(celdas).replace("-", "$-$") + r" \\")
    with open(os.path.join(CARPETA, "tabla_resultados.tex"), "w", encoding="utf8") as fh:
        fh.write("\n".join(lineas) + "\n")


def imprimir(tabla, mx):
    print(f"{'th2[°]':>7} {'t[s]':>6} {'xP[mm]':>7} {'yP[mm]':>7} {'w2':>6} {'a2':>7} {'|vP|':>6} {'|aP|':>6}")
    for f in tabla:
        f = [f[0]] + [round(v, 3) + 0.0 for v in f[1:]]
        print(f"{f[0]:>7d} {f[1]:6.3f} {f[2]:7.1f} {f[3]:7.1f} {f[4]:6.3f} {f[5]:7.3f} {f[6]:6.3f} {f[7]:6.3f}")
    print(f"\nMáximos: omega2 = {mx['omega2']:.3f} rad/s ({mx['omega2'] * 60 / (2 * np.pi):.1f} rpm), "
          f"alpha2 = {mx['alpha2']:.3f} rad/s²")
    print(f"         |vP| = {mx['vP']:.3f} m/s en theta2 = {mx['theta2_vP']:.0f}° (t = {mx['t_vP']:.2f} s)")
    print(f"         |aP| = {mx['aP']:.3f} m/s² en theta2 = {mx['theta2_aP']:.0f}° (t = {mx['t_aP']:.2f} s)")


if __name__ == "__main__":
    tabla = filas()
    guardar(tabla)
    imprimir(tabla, maximos())
