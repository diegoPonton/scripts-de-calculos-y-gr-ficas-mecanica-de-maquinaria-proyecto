"""
Gráficas del informe del Avance 3.

    figuras/fig_trayectoria   Figura 1: trayectorias de A y P, mecanismo cada 60°
    figuras/fig_estado35      Figura 2: velocidades y aceleraciones en theta2 = 35°
    figuras/fig_gripper       Figura 3: velocidad y aceleración de P en la maniobra
    figuras/fig_maniobra      Extra: theta2, omega2 y alpha2 del brazo vs tiempo

Cada figura se guarda en PNG y PDF.

Uso:  python graficas.py
"""
import os

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon, Rectangle, FancyArrowPatch, Wedge

from parametros import L, R_TRASERA, E, T, THETA2_INICIAL, RECORRIDO
from cinematica import estado, ley_cicloidal
from posicion_estudio import calcular as calcular_estudio

CARPETA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figuras")
R = R_TRASERA

# Estilo
C1, C2, C3 = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#d9d8d4"
plt.rcParams.update({
    "font.family": "serif", "font.serif": ["DejaVu Serif"], "mathtext.fontset": "cm",
    "font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK, "axes.linewidth": 0.6,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.5,
    "xtick.color": INK2, "ytick.color": INK2, "lines.linewidth": 1.6,
    "legend.frameon": False, "savefig.dpi": 200,
})


def guardar(fig, nombre):
    os.makedirs(CARPETA, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(CARPETA, f"{nombre}.{ext}"), bbox_inches="tight")
    plt.close(fig)


def flecha(ax, p, v, color, lw=1.6, label=None):
    ax.add_patch(FancyArrowPatch(p, (p[0] + v[0], p[1] + v[1]), arrowstyle="-|>",
                                 mutation_scale=9, color=color, lw=lw, zorder=6))
    if label:
        ax.plot([], [], color=color, lw=lw, label=label)


def dibujar_mecanismo(ax, theta2, alpha=1.0, lw=1.0):
    """Brazo, poleas, correa y gripper a escala (mm)."""
    A = np.array([L * np.cos(theta2), L * np.sin(theta2)])
    u = A / L
    n = np.array([-u[1], u[0]])
    for sg in (1, -1):   # ramales de la correa
        p0, p1 = sg * R * n, A + sg * R * n
        ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color=INK2, lw=0.8 * lw, alpha=alpha, zorder=2)
    ax.plot([0, A[0]], [0, A[1]], color=INK, lw=2.4 * lw, alpha=alpha, solid_capstyle="round", zorder=3)
    ax.add_patch(Circle((0, 0), R, fc="#e9e8e4", ec=INK, lw=0.8, alpha=alpha, zorder=4))
    ax.add_patch(Circle(A, R, fc="white", ec=INK, lw=0.8, alpha=alpha, zorder=4))
    ax.plot([A[0] - R, A[0] + R], [A[1], A[1]], color=INK, lw=0.7, alpha=alpha, zorder=5)
    # gripper (siempre horizontal)
    ax.add_patch(Rectangle((A[0] + R, A[1] - 3), 55 - R, 6, fc="white", ec=INK, lw=0.7, alpha=alpha, zorder=4))
    ax.add_patch(Rectangle((A[0] + 55, A[1] - 22), 14, 44, fc="white", ec=INK, lw=0.7, alpha=alpha, zorder=4))
    for sg in (1, -1):
        ax.add_patch(Polygon([[A[0] + 69, A[1] + sg * 8], [A[0] + 69, A[1] + sg * 20],
                              [A[0] + E, A[1] + sg * 16], [A[0] + E, A[1] + sg * 10]],
                             closed=True, fc="white", ec=INK, lw=0.7, alpha=alpha, zorder=4))


def figura_trayectoria():
    fig, ax = plt.subplots(figsize=(6.4, 4.6))
    ang = np.linspace(THETA2_INICIAL, THETA2_INICIAL + RECORRIDO, 400)
    ax.plot(L * np.cos(ang), L * np.sin(ang), color=C3, lw=1.2,
            label="Trayectoria de $A$ (centro de la polea delantera)")
    ax.plot(L * np.cos(ang) + E, L * np.sin(ang), color=C1, lw=1.6,
            label="Trayectoria de $P$ (punta de los dedos)")
    for deg in range(-60, 241, 60):
        dibujar_mecanismo(ax, np.deg2rad(deg), alpha=0.6, lw=0.8)
    ax.add_patch(Wedge((0, 0), 125, -120, -60, fc="#f3d9cf", ec="none", zorder=0))
    ax.text(0, -132, "sector\nbloqueado\n(60°)", ha="center", va="top", fontsize=7.5, color=INK2,
            bbox=dict(fc="white", ec="none", pad=1.0, alpha=0.85), zorder=8)
    ax.plot(0, 0, "+", color=INK, ms=8)
    ax.set_aspect("equal")
    ax.set_xlabel("x [mm]")
    ax.set_ylabel("y [mm]")
    ax.set_xlim(-420, 470)
    ax.set_ylim(-300, 345)
    ax.legend(loc="upper right", fontsize=7.5)
    guardar(fig, "fig_trayectoria")


def figura_estado35():
    s = calcular_estudio()
    th = s["theta2"]
    A, P, G = s["r_A"], s["r_P"], s["r_G2"]
    sv, sa = 120.0, 60.0   # mm de dibujo por m/s y por m/s^2
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.2))
    for k, ax in enumerate(axs):
        dibujar_mecanismo(ax, th)
        ax.set_aspect("equal")
        ax.set_xlim(-45, 445)
        ax.set_ylim(-60, 290)
        ax.grid(False)
        ax.set_xticks([])
        ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_visible(False)
        g_off = (-26, 4) if k == 0 else (8, -18)
        for nombre, p, off in (("$O_2$", (0, 0), (-22, -24)), ("$A$", A, (4, -26)),
                               ("$P$", P, (4, -22)), ("$G_2$", G, g_off)):
            ax.plot(*p, "o", ms=3.5, color=INK, zorder=7)
            ax.annotate(nombre, p, xytext=off, textcoords="offset points", fontsize=9)
        ax.plot([0, 70], [0, 0], color=INK2, lw=0.6, ls=":")
        ax.annotate("", xy=(55 * np.cos(th), 55 * np.sin(th)), xytext=(55, 0),
                    arrowprops=dict(arrowstyle="-", color=INK2, lw=0.6, connectionstyle="arc3,rad=0.25"))
        ax.text(64, 8, r"$\theta_2=35^\circ$", fontsize=8, color=INK2)
    flecha(axs[0], A, sv * s["v_A"], C1, label=r"$\mathbf{v}_A=\mathbf{v}_B=\mathbf{v}_P$")
    flecha(axs[0], P, sv * s["v_P"], C1)
    flecha(axs[0], G, sv * s["v_G2"], C3, label=r"$\mathbf{v}_{G_2}$")
    axs[0].set_title(f"(a) Velocidades  (escala: 100 mm = {100 / sv:.2f} m/s)", fontsize=8.5)
    axs[0].legend(loc="upper left", fontsize=8)
    flecha(axs[1], A, sa * s["a_t"], C3, lw=1.1, label=r"$a^t_A=L\alpha_2$")
    flecha(axs[1], A, sa * s["a_n"], C2, lw=1.1, label=r"$a^n_A=L\omega_2^2$")
    flecha(axs[1], A, sa * s["a_A"], C1, label=r"$\mathbf{a}_A=\mathbf{a}_P$")
    flecha(axs[1], P, sa * s["a_P"], C1)
    axs[1].set_title(f"(b) Aceleraciones  (escala: 100 mm = {100 / sa:.2f} m/s²)", fontsize=8.5)
    axs[1].legend(loc="upper left", fontsize=8)
    fig.tight_layout()
    guardar(fig, "fig_estado35")


def _series(n=3001):
    tt = np.linspace(0, T, n)
    est = [estado(t) for t in tt]
    return tt, est


def figura_gripper(tt, est):
    t35 = calcular_estudio()["t"]
    vP = np.array([s["v_P"] for s in est])
    aP = np.array([s["a_P"] for s in est])
    fig, axs = plt.subplots(2, 1, figsize=(6.4, 4.6), sharex=True)
    axs[0].plot(tt, vP[:, 0], color=C1, label=r"$v_{Px}$")
    axs[0].plot(tt, vP[:, 1], color=C2, label=r"$v_{Py}$")
    axs[0].plot(tt, np.linalg.norm(vP, axis=1), color=C3, label=r"$|\mathbf{v}_P|$")
    axs[0].set_ylabel("Velocidad [m/s]")
    axs[1].plot(tt, aP[:, 0], color=C1, label=r"$a_{Px}$")
    axs[1].plot(tt, aP[:, 1], color=C2, label=r"$a_{Py}$")
    axs[1].plot(tt, np.linalg.norm(aP, axis=1), color=C3, label=r"$|\mathbf{a}_P|$")
    axs[1].set_ylabel("Aceleración [m/s²]")
    axs[1].set_xlabel("t [s]")
    for ax in axs:
        ax.axhline(0, color=INK2, lw=0.5)
        ax.axvline(t35, color=INK2, lw=0.6, ls=":")
        ax.legend(loc="lower left", ncol=3, fontsize=8)
    fig.align_ylabels(axs)
    fig.tight_layout()
    guardar(fig, "fig_gripper")


def figura_maniobra(tt):
    th, w, a = ley_cicloidal(tt)
    fig, axs = plt.subplots(3, 1, figsize=(6.4, 5.0), sharex=True)
    axs[0].plot(tt, np.rad2deg(th), color=C1)
    axs[0].set_ylabel(r"$\theta_2$ [°]")
    axs[0].set_yticks([-60, 0, 90, 180, 240])
    axs[1].plot(tt, w, color=C1)
    axs[1].set_ylabel(r"$\omega_2=\omega_4$ [rad/s]")
    axs[2].plot(tt, a, color=C1)
    axs[2].axhline(0, color=INK2, lw=0.5)
    axs[2].set_ylabel(r"$\alpha_2=\alpha_4$ [rad/s²]")
    axs[2].set_xlabel("t [s]")
    fig.align_ylabels(axs)
    fig.tight_layout()
    guardar(fig, "fig_maniobra")


def generar_todas():
    tt, est = _series()
    figura_trayectoria()
    figura_estado35()
    figura_gripper(tt, est)
    figura_maniobra(tt)
    print(f"Figuras guardadas en {CARPETA}")


if __name__ == "__main__":
    generar_todas()
