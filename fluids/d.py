# Plot u_theta(r) and omega(r) along a centerline (x-axis, y=0) for the Lamb–Oseen vortex
# using nu=1, Gamma=1 at times t=0.01, 0.1, 1.
# Follow tool rules: matplotlib only, one chart per figure, no explicit colors.
import numpy as np
import matplotlib.pyplot as plt
import os

nu = 1.0
Gamma = 1.0
times = [0.01, 0.1, 1.0]

# Create output directory if it doesn't exist
output_dir = "output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# radial coordinate along the centerline (positive x-axis)
r = np.linspace(0, 5, 400)

def u_theta(r, t, nu=nu, Gamma=Gamma):
    # handle r=0 limit safely
    r_safe = np.where(r==0, 1e-15, r)
    return (Gamma/(2*np.pi*r_safe)) * (1 - np.exp(-r**2/(4*nu*t)))

def omega(r, t, nu=nu, Gamma=Gamma):
    return (Gamma/(4*np.pi*nu*t)) * np.exp(-r**2/(4*nu*t))

# Plot u_theta profiles
plt.figure(figsize=(7,5))
colors = ['blue', 'red', 'green']
for i, t in enumerate(times):
    plt.plot(r, u_theta(r,t), label=f't={t}', color=colors[i])
plt.xlabel('r (distance from center)')
plt.ylabel(r'$u_\theta$ (tangential speed)')
plt.title('Tangential Speed vs radius along centerline')
plt.legend()
path1 = os.path.join(output_dir, 'utheta_profiles.png')
plt.tight_layout()
plt.savefig(path1, dpi=160)
plt.show()

# Plot omega profiles
plt.figure(figsize=(7,5))
colors = ['blue', 'red', 'green']
for i, t in enumerate(times):
    plt.plot(r, omega(r,t), label=f't={t}', color=colors[i])
plt.xlabel('r (distance from center)')
plt.ylabel(r'$\omega$ (vorticity, z-component)')
plt.title('Vorticity vs radius along centerline')
plt.legend()
path2 = os.path.join(output_dir, 'omega_profiles.png')
plt.tight_layout()
plt.savefig(path2, dpi=160)
plt.show()

print("Generated files:")
print(f"  {path1}")
print(f"  {path2}")

[path1, path2]
