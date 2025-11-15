# Beautiful Modeling Demo: Gray–Scott Reaction–Diffusion (pure NumPy)
# ---------------------------------------------------------------
# pip install numpy matplotlib
#
# PDE model:
#   ∂U/∂t = D_u ∇²U - U V² + F (1 - U)
#   ∂V/∂t = D_v ∇²V + U V² - (F + k) V
# where U, V are concentrations; D_u, D_v are diffusion rates; F is feed; k is kill.
# This simple model produces rich Turing patterns found in nature.

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# ---------------- simulation parameters ----------------
N = 256              # grid size (try 384 if your machine is fast)
Du, Dv = 0.16, 0.08  # diffusion rates
dt = 1.0             # time step (CFL-stable for this Laplacian)
steps_per_frame = 10 # more steps between frames = faster evolution

# Presets (F, k) for different pattern regimes
PRESETS = {
    "1: Solitons" : (0.030, 0.062),
    "2: Mitosis"  : (0.0367, 0.0649),
    "3: Worms"    : (0.022, 0.051),
    "4: Mazes"    : (0.029, 0.057),
    "5: Chaos"    : (0.040, 0.060),
}

preset_name = "3: Worms"
F, k = PRESETS[preset_name]

# ---------------- helpers ----------------
def laplacian(Z):
    # Periodic 5-point Laplacian via roll (no SciPy needed)
    return (
        -4*Z
        + np.roll(Z, 1, 0) + np.roll(Z, -1, 0)
        + np.roll(Z, 1, 1) + np.roll(Z, -1, 1)
    )

def seed(U, V, kind="random"):
    U[:] = 1.0; V[:] = 0.0
    # central square seeded with V
    r = N//10
    c = slice(N//2 - r, N//2 + r)
    U[c, c] = 0.50; V[c, c] = 0.25
    if kind == "random":
        U += 0.05*np.random.rand(N, N)
        V += 0.05*np.random.rand(N, N)

# ---------------- initialize fields ----------------
U = np.ones((N, N), dtype=np.float32)
V = np.zeros((N, N), dtype=np.float32)
seed(U, V)

# ---------------- figure ----------------
plt.style.use("dark_background")
fig, ax = plt.subplots(figsize=(6.8, 6.8))
im = ax.imshow(V, cmap="magma", interpolation="bicubic", vmin=0, vmax=1)
ax.set_xticks([]); ax.set_yticks([])
title = ax.set_title(
    f"Gray–Scott Reaction–Diffusion  |  {preset_name}  (F={F:.4f}, k={k:.4f})",
    pad=10
)

# ---------------- keyboard controls ----------------
info = (
    "Keys: 1–5 presets • r reseed • [ / ] adjust F • { / } adjust k • p pause • s save PNG"
)
txt = fig.text(0.5, 0.02, info, ha="center", va="bottom", fontsize=9, alpha=0.9)

paused = False
def on_key(event):
    global F, k, preset_name, paused
    if event.key in "12345":
        idx = int(event.key)
        preset_name = [k for k in PRESETS.keys()][idx-1]
        F, k = PRESETS[preset_name]
        seed(U, V)
    elif event.key == "r":
        seed(U, V)
    elif event.key == "[":
        F = max(0.0, F - 0.0005)
    elif event.key == "]":
        F = min(0.08, F + 0.0005)
    elif event.key == "{":
        k = max(0.0, k - 0.0005)
    elif event.key == "}":
        k = min(0.08, k + 0.0005)
    elif event.key == "p":
        paused = not paused
    elif event.key == "s":
        fig.savefig("gray_scott.png", dpi=300, bbox_inches="tight")
        print("Saved gray_scott.png")
    title.set_text(f"Gray–Scott Reaction–Diffusion  |  {preset_name}  (F={F:.4f}, k={k:.4f})")

fig.canvas.mpl_connect("key_press_event", on_key)

# ---------------- time stepping ----------------
def step():
    global U, V
    Lu = laplacian(U)
    Lv = laplacian(V)
    UVV = U*V*V
    U += (Du*Lu - UVV + F*(1 - U)) * dt
    V += (Dv*Lv + UVV - (F + k)*V) * dt
    # keep numbers in bounds (helps stability/visuals)
    np.clip(U, 0, 1, out=U)
    np.clip(V, 0, 1, out=V)

def update(_):
    if not paused:
        for _ in range(steps_per_frame):
            step()
    im.set_data(V)
    return (im,)

ani = FuncAnimation(fig, update, interval=30, blit=True)
plt.show()
