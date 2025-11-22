# script_3_ricci.py

import sympy as sp

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
    term1 = sp.diff(Gamma[mu][nu][sigma], coords[rho])
    term2 = sp.diff(Gamma[mu][nu][rho], coords[sigma])
    term3 = 0
    term4 = 0
    for lam in range(4):
        term3 += Gamma[mu][lam][rho] * Gamma[lam][nu][sigma]
        term4 += Gamma[mu][lam][sigma] * Gamma[lam][nu][rho]
    return sp.simplify(term1 - term2 + term3 - term4)

# Precompute Riemann with one index up
Riemann = [[[[None for _ in range(4)] for _ in range(4)]
            for _ in range(4)] for _ in range(4)]
for mu in range(4):
    for nu in range(4):
        for rho in range(4):
            for sigma in range(4):
                Riemann[mu][nu][rho][sigma] = Riemann_symbol(mu, nu, rho, sigma)

# Ricci: R_{νσ} = R^μ_{νμσ}
Ricci = [[None for _ in range(4)] for _ in range(4)]
for nu in range(4):
    for sigma in range(4):
        s = 0
        for mu in range(4):
            s += Riemann[mu][nu][mu][sigma]
        Ricci[nu][sigma] = sp.simplify(s)

# Extract components of interest
R_tt = sp.simplify(Ricci[0][0])
R_rr = sp.simplify(Ricci[1][1])
R_tr = sp.simplify(Ricci[0][1])  # = R_rt
R_thth = sp.simplify(Ricci[2][2])
R_phph = sp.simplify(Ricci[3][3])

print("R_tt =", R_tt)
print("R_rr =", R_rr)
print("R_tr =", R_tr)
print("R_θθ =", R_thth)
print("R_φφ =", R_phph)
