"""
Ejecuta todo el análisis del Avance 3 y genera los archivos del informe.

    python main.py

Salidas:
    resultados/tabla_resultados.csv   tabla cada 30°
    resultados/tabla_resultados.tex   filas de la Tabla 2 del informe
    resultados/valores.tex            números citados en el informe
    figuras/*.png, figuras/*.pdf      figuras del informe
"""
import os

import numpy as np

import parametros as p
import posicion_estudio
import tabla_resultados
import graficas
import verificacion

CARPETA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultados")


def escribir_valores(s, mx):
    """Macros de LaTeX con los valores que se citan en el texto del informe."""
    n = np.linalg.norm
    valores = {
        "Lmm": f"{p.L:.0f}", "rmm": f"{p.R_TRASERA:.0f}", "emm": f"{p.E:.0f}", "Tman": f"{p.T:.1f}",
        "test": f"{s['t']:.3f}", "west": f"{s['omega2']:.3f}", "aest": f"{s['alpha2']:.3f}",
        "xAest": f"{s['r_A'][0]:.1f}", "yAest": f"{s['r_A'][1]:.1f}", "xPest": f"{s['r_P'][0]:.1f}",
        "vAxest": f"{s['v_A'][0]:.3f}", "vAyest": f"{s['v_A'][1]:.3f}", "vAest": f"{n(s['v_A']):.3f}",
        "atest": f"{n(s['a_t']):.3f}", "anest": f"{n(s['a_n']):.3f}",
        "aAxest": f"{s['a_A'][0]:.3f}", "aAyest": f"{s['a_A'][1]:.3f}", "aAest": f"{n(s['a_A']):.3f}",
        "wmax": f"{mx['omega2']:.3f}", "amax": f"{mx['alpha2']:.3f}",
        "vPmax": f"{mx['vP']:.3f}", "aPmax": f"{mx['aP']:.3f}",
    }
    lineas = ["% Generado por main.py - no editar a mano"]
    lineas += [f"\\newcommand{{\\v{k}}}{{{v}}}" for k, v in valores.items()]
    with open(os.path.join(CARPETA, "valores.tex"), "w", encoding="utf8") as fh:
        fh.write("\n".join(lineas) + "\n")


def main():
    os.makedirs(CARPETA, exist_ok=True)

    s = posicion_estudio.calcular()
    posicion_estudio.imprimir(s)

    print("\n" + "=" * 64 + "\nRESULTADOS CADA 30°\n" + "=" * 64)
    tabla = tabla_resultados.filas()
    mx = tabla_resultados.maximos()
    tabla_resultados.guardar(tabla)
    tabla_resultados.imprimir(tabla, mx)

    print()
    verificacion.ejecutar()

    print()
    graficas.generar_todas()
    escribir_valores(s, mx)
    print(f"Resultados guardados en {CARPETA}")


if __name__ == "__main__":
    main()
