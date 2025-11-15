# POWER DEMO (Python): Chaotic Double Pendulum + Lyapunov Exponent
# Requirements: numpy, scipy, matplotlib
#   pip install numpy scipy matplotlib

import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.gridspec as gridspec

# ---------------- Parameters ----------------
g  = 9.81
m1 = 1.0; m2 = 1.0
L1 = 1.0; L2 = 1.0
TFinal = 30.0
FPS = 60
eps = 1e-6  # tiny angular perturbation

y0a = np.array([np.pi/2, 0.0, 0.0, 0.0])          # [theta1, omega1, theta2, omega2]
y0b = np.array([np.pi/2 + eps, 0.0, 0.0, 0.0])

t_eval = np.linspace(0, TFinal, int(TFinal*FPS))

# ---------------- Dynamics ----------------
def f(t, y):
    th1, w1, th2, w2 = y
    d = th1 - th2

    den1 = L1 * (2*m1 + m2 - m2*np.cos(2*th1 - 2*th2))
    den2 = L2 * (2*m1 + m2 - m2*np.cos(2*th1 - 2*th2))

    dw1 = ( -g*(2*m1+m2)*np.sin(th1)
            - m2*g*np.sin(th1-2*th2)
            - 2*np.sin(d)*m2*(w2**2*L2 + w1**2*L1*np.cos(d)) ) / den1

    dw2 = ( 2*np.sin(d)*( w1**2*L1*(m1+m2)
            + g*(m1+m2)*np.cos(th1)
            + w2**2*L2*m2*np.cos(d) ) ) / den2

    return np.array([w1, dw1, w2, dw2])

def to_xy(th1, th2):
    x1 =  L1*np.sin(th1);  y1 = -L1*np.cos(th1)
    x2 =  x1 + L2*np.sin(th2)
    y2 =  y1 - L2*np.cos(th2)
    return x1, y1, x2, y2

# ---------------- Integrate both trajectories ----------------
solA = solve_ivp(f, [0, TFinal], y0a, t_eval=t_eval, rtol=1e-9, atol=1e-9)
solB = solve_ivp(f, [0, TFinal], y0b, t_eval=t_eval, rtol=1e-9, atol=1e-9)

th1a, w1a, th2a, w2a = solA.y
th1b, _,   th2b, _   = solB.y
t = solA.t

x1a,y1a,x2a,y2a = to_xy(th1a, th2a)
x1b,y1b,x2b,y2b = to_xy(th1b, th2b)

# Divergence measure (in angle space) and its log
delta = np.sqrt((th1a - th1b)**2 + (th2a - th2b)**2)
lnDelta = np.log(delta/eps)

# Fit early linear region for Lyapunov estimate (first ~6 s)
fitN = np.searchsorted(t, 6.0)
p = np.polyfit(t[:fitN], lnDelta[:fitN], 1)
lambda_est = p[0]
fit_y = np.polyval(p, t[:fitN])

# ---------------- Figure & Artists ----------------
plt.style.use('dark_background')
fig = plt.figure("Chaotic Double Pendulum", figsize=(10,5))
gs = gridspec.GridSpec(1,2, figure=fig, wspace=0.18)

# Left: animation
ax1 = fig.add_subplot(gs[0,0])
ax1.set_title("Chaotic Double Pendulum (two starts, Δθ = 10⁻⁶)")
ax1.set_aspect('equal', adjustable='box')
R = L1 + L2
ax1.set_xlim(-R, R); ax1.set_ylim(-R, R)
ax1.grid(False)
# A (blue/white) and B (red) systems
(rodA1,) = ax1.plot([0, x1a[0]], [0, y1a[0]], '-', lw=2, color=(0.9,0.9,1))
(rodA2,) = ax1.plot([x1a[0], x2a[0]], [y1a[0], y2a[0]], '-', lw=2, color=(0.6,0.8,1))
(bobA1,) = ax1.plot(x1a[0], y1a[0], 'o', ms=6, mfc=(0.8,0.9,1), mec='none')
(bobA2,) = ax1.plot(x2a[0], y2a[0], 'o', ms=8, mfc=(0.4,0.7,1), mec='none')

(rodB1,) = ax1.plot([0, x1b[0]], [0, y1b[0]], '-', lw=2, color=(1.0,0.9,0.9))
(rodB2,) = ax1.plot([x1b[0], x2b[0]], [y1b[0], y2b[0]], '-', lw=2, color=(1.0,0.6,0.6))
(bobB1,) = ax1.plot(x1b[0], y1b[0], 'o', ms=6, mfc=(1,0.85,0.85), mec='none')
(bobB2,) = ax1.plot(x2b[0], y2b[0], 'o', ms=8, mfc=(1,0.55,0.55), mec='none')

trail_len = 300
trailA, = ax1.plot([], [], '-', lw=1.2, alpha=0.9, color=(0.3,0.7,1))
trailB, = ax1.plot([], [], '-', lw=1.2, alpha=0.9, color=(1,0.4,0.4))

# Right: divergence + fit
ax2 = fig.add_subplot(gs[0,1])
ax2.set_title("Divergence & Lyapunov Estimate")
ax2.set_xlabel("Time (s)")
ax2.set_ylabel("ln(Δ/ε)")
curve, = ax2.plot([], [], 'w-', lw=1.5)
fit_line, = ax2.plot(t[:fitN], fit_y, '--', lw=1.5, color=(0.6,0.8,1))
txt = ax2.text(0.02, 0.95, f"λ ≈ {lambda_est:.3f} s⁻¹",
               transform=ax2.transAxes, ha='left', va='top', fontsize=12)

ax2.set_xlim(0, t[-1])
ymin = np.nanmin(lnDelta[:fitN]) - 0.5
ymax = np.nanmax(lnDelta[:fitN]) + 0.5
ax2.set_ylim(ymin, max(ymax, 5))

# ---------------- Animation function ----------------
xA_hist, yA_hist = [], []
xB_hist, yB_hist = [], []

def update(k):
    # left: update rods/bobs
    rodA1.set_data([0, x1a[k]], [0, y1a[k]])
    rodA2.set_data([x1a[k], x2a[k]], [y1a[k], y2a[k]])
    bobA1.set_data([x1a[k]], [y1a[k]])
    bobA2.set_data([x2a[k]], [y2a[k]])

    rodB1.set_data([0, x1b[k]], [0, y1b[k]])
    rodB2.set_data([x1b[k], x2b[k]], [y1b[k], y2b[k]])
    bobB1.set_data([x1b[k]], [y1b[k]])
    bobB2.set_data([x2b[k]], [y2b[k]])

    # trails
    xA_hist.append(x2a[k]); yA_hist.append(y2a[k])
    xB_hist.append(x2b[k]); yB_hist.append(y2b[k])
    if len(xA_hist) > trail_len:
        del xA_hist[0]; del yA_hist[0]; del xB_hist[0]; del yB_hist[0]
    trailA.set_data(xA_hist, yA_hist)
    trailB.set_data(xB_hist, yB_hist)

    # right: divergence up to k
    curve.set_data(t[:k+1], lnDelta[:k+1])
    return (rodA1, rodA2, bobA1, bobA2,
            rodB1, rodB2, bobB1, bobB2,
            trailA, trailB, curve)

ani = FuncAnimation(fig, update, frames=len(t), interval=1000/FPS, blit=True)
plt.show()
