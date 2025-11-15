# Lamb–Oseen vortex velocity field quiver plots in Python
# Requirements from the prompt:
# - Use matplotlib (no seaborn), each chart its own plot, no explicit colors.
# - Domain: x,y in [-5, 5].
# - Parameters: nu = 1, Gamma = 1.
# - Times to plot: t = 0.01, 0.1, 1.
# - Transform from polar to Cartesian: u = ur*cosθ - uθ*sinθ; v = ur*sinθ + uθ*cosθ.
#   For Lamb–Oseen, ur = 0.
#
# We'll make one quiver plot per time.
import numpy as np
import matplotlib.pyplot as plt
import os

# Parameters
nu = 1.0
Gamma = 1.0
times = [0.01, 0.1, 1.0]

# Grid
n = 41  # resolution
x = np.linspace(-5, 5, n)
y = np.linspace(-5, 5, n)
X, Y = np.meshgrid(x, y)

# Polar coordinates
R = np.hypot(X, Y)           # r >= 0
Theta = np.arctan2(Y, X)     # theta in [-pi, pi]

# A tiny epsilon to avoid division by zero in formulas that use 1/r
eps = 1e-12
R_safe = np.where(R == 0, eps, R)

# Create output directory if it doesn't exist
output_dir = "output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Loop over times, compute u_theta and then (u,v), and make one plot per time.
fig_paths = []
for t in times:
    # Lamb–Oseen u_theta(r,t)
    u_theta = (Gamma/(2*np.pi*R_safe)) * (1 - np.exp(-(R**2)/(4*nu*t)))
    
    # u_r = 0 for this model
    u_r = np.zeros_like(R)
    
    # Convert to Cartesian: u = ur*cosθ - uθ*sinθ; v = ur*sinθ + uθ*cosθ
    U = u_r*np.cos(Theta) - u_theta*np.sin(Theta)
    V = u_r*np.sin(Theta) + u_theta*np.cos(Theta)
    
    # Make a quiver plot
    plt.figure(figsize=(6, 6))
    plt.quiver(X, Y, U, V, angles='xy', scale_units='xy', scale=3.0, width=0.003)
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title(f'At t={t})')
    plt.axis('equal')
    plt.xlim([-5,5])
    plt.ylim([-5,5])
    path = os.path.join(output_dir, f'lamb_oseen_quiver_t_{str(t).replace(".","p")}.png')
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.show()
    fig_paths.append(path)

print("Generated files:")
for path in fig_paths:
    print(f"  {path}")
