# script_2_riemann.py

import sympy as sp

# Rebuild everything (so this script is standalone)
t, r, theta, phi = sp.symbols('t r theta phi', real=True)
coords = [t, r, theta, phi]

alpha = sp.Function('alpha')(t, r)
beta  = sp.Function('beta')(t, r)

g = sp.diag(
    -sp.exp(2*alpha),
     sp.exp(2*beta),
     r**2,
     r**2*sp.sin(theta)**2
)

g_inv = sp.simplify(g.inv())

def Gamma_symbol(mu, nu, rho):
    result = 0
    for lam in range(4):
        term = (
            sp.diff(g[lam, rho], coords[nu])
            + sp.diff(g[lam, nu], coords[rho])
            - sp.diff(g[nu, rho], coords[lam])
        )
        result += g_inv[mu, lam] * term
    return sp.simplify(sp.Rational(1, 2)*result)

Gamma = [[ [None for _ in range(4)] for _ in range(4)] for _ in range(4)]
for mu in range(4):
    for nu in range(4):
        for rho in range(4):
            Gamma[mu][nu][rho] = Gamma_symbol(mu, nu, rho)

def Riemann_symbol(mu, nu, rho, sigma):
    """
    R^μ_{νρσ} = ∂_ρ Γ^μ_{νσ} - ∂_σ Γ^μ_{νρ}
               + Γ^μ_{λρ} Γ^λ_{νσ} - Γ^μ_{λσ} Γ^λ_{νρ}
    """
    term1 = sp.diff(Gamma[mu][nu][sigma], coords[rho])
    term2 = sp.diff(Gamma[mu][nu][rho], coords[sigma])
    term3 = 0
    term4 = 0
    for lam in range(4):
        term3 += Gamma[mu][lam][rho] * Gamma[lam][nu][sigma]
        term4 += Gamma[mu][lam][sigma] * Gamma[lam][nu][rho]
    return sp.simplify(term1 - term2 + term3 - term4)

Riemann = [[[[None for _ in range(4)] for _ in range(4)]
            for _ in range(4)] for _ in range(4)]

for mu in range(4):
    for nu in range(4):
        for rho in range(4):
            for sigma in range(4):
                Riemann[mu][nu][rho][sigma] = Riemann_symbol(mu, nu, rho, sigma)

print("Selected Riemann components (one index up):")
# Indices: 0=t, 1=r, 2=θ, 3=φ

R_t_r_t_r = Riemann[0][1][0][1]
print("R^t_{r t r} =", sp.simplify(R_t_r_t_r))

R_t_theta_t_theta = Riemann[0][2][0][2]
print("R^t_{θ t θ} =", sp.simplify(R_t_theta_t_theta))

R_t_phi_t_phi = Riemann[0][3][0][3]
print("R^t_{φ t φ} =", sp.simplify(R_t_phi_t_phi))

R_r_theta_r_theta = Riemann[1][2][1][2]
print("R^r_{θ r θ} =", sp.simplify(R_r_theta_r_theta))

R_r_phi_r_phi = Riemann[1][3][1][3]
print("R^r_{φ r φ} =", sp.simplify(R_r_phi_r_phi))

R_theta_phi_theta_phi = Riemann[2][3][2][3]
print("R^θ_{φ θ φ} =", sp.simplify(R_theta_phi_theta_phi))
