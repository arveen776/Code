# script_1_christoffel.py

import sympy as sp

# ----------------------------------------------------
# 1. Coordinates and metric functions
# ----------------------------------------------------
t, r, theta, phi = sp.symbols('t r theta phi', real=True)
coords = [t, r, theta, phi]

alpha = sp.Function('alpha')(t, r)
beta  = sp.Function('beta')(t, r)

# Metric:
# ds^2 = -e^{2α} dt^2 + e^{2β} dr^2 + r^2 dθ^2 + r^2 sin^2θ dφ^2
g = sp.diag(
    -sp.exp(2*alpha),      # g_tt
     sp.exp(2*beta),       # g_rr
     r**2,                 # g_θθ
     r**2*sp.sin(theta)**2 # g_φφ
)

# Inverse metric
g_inv = sp.simplify(g.inv())

# ----------------------------------------------------
# 2. Christoffel symbols Γ^μ_{νρ}
# ----------------------------------------------------
def Gamma_symbol(mu, nu, rho):
    """
    Compute Christoffel symbol Γ^μ_{νρ} using the standard formula:
    Γ^μ_{νρ} = 1/2 g^{μλ} (∂_ν g_{λρ} + ∂_ρ g_{λν} - ∂_λ g_{νρ})
    Indices: mu,nu,rho = 0..3 corresponding to t,r,θ,φ.
    """
    lam = sp.symbols('lam', integer=True)
    result = 0
    for lam in range(4):
        term = (
            sp.diff(g[lam, rho], coords[nu])
            + sp.diff(g[lam, nu], coords[rho])
            - sp.diff(g[nu, rho], coords[lam])
        )
        result += g_inv[mu, lam] * term
    return sp.simplify(sp.Rational(1, 2)*result)

# Precompute all Γ^μ_{νρ}
Gamma = [[ [None for _ in range(4)] for _ in range(4)] for _ in range(4)]
for mu in range(4):
    for nu in range(4):
        for rho in range(4):
            Gamma[mu][nu][rho] = Gamma_symbol(mu, nu, rho)

# ----------------------------------------------------
# 3. Print the key nonzero Γ components to compare with Carroll (5.39)
#    Indices map: 0=t, 1=r, 2=θ, 3=φ
# ----------------------------------------------------
print("Non-zero Christoffel symbols (schematically):\n")

Γ = Gamma  # just a shorter alias

# Γ^t_{tt} = ∂_t α
print("Γ^t_{tt} =", Γ[0][0][0])

# Γ^t_{tr} = Γ^t_{rt} = ∂_r α
print("Γ^t_{tr} =", Γ[0][0][1])

# Γ^t_{rr} = e^{2(β-α)} ∂_t β
print("Γ^t_{rr} =", Γ[0][1][1])

# Γ^r_{tt} = e^{2(α-β)} ∂_r α
print("Γ^r_{tt} =", Γ[1][0][0])

# Γ^r_{tr} = Γ^r_{rt} = ∂_t β
print("Γ^r_{tr} =", Γ[1][0][1])

# Γ^r_{rr} = ∂_r β
print("Γ^r_{rr} =", Γ[1][1][1])

# Γ^θ_{rθ} = Γ^θ_{θr} = 1/r
print("Γ^θ_{rθ} =", Γ[2][1][2])

# Γ^r_{θθ} = -r e^{-2β}
print("Γ^r_{θθ} =", Γ[1][2][2])

# Γ^φ_{rφ} = Γ^φ_{φr} = 1/r
print("Γ^φ_{rφ} =", Γ[3][1][3])

# Γ^r_{φφ} = -r e^{-2β} sin^2θ
print("Γ^r_{φφ} =", Γ[1][3][3])

# Γ^θ_{φφ} = -sinθ cosθ
print("Γ^θ_{φφ} =", Γ[2][3][3])

# Γ^φ_{θφ} = Γ^φ_{φθ} = cotθ
print("Γ^φ_{θφ} =", Γ[3][2][3])
