# script_4_schwarzschild.py

import sympy as sp

# ----------------------------------------------------
# 1. Static spherically symmetric metric: α(r), β(r)
# ----------------------------------------------------
r, theta, phi = sp.symbols('r theta phi', real=True)
t = sp.symbols('t', real=True)
coords = [t, r, theta, phi]

A = sp.Function('A')(r)  # A(r) = α(r)
B = sp.Function('B')(r)  # B(r) = β(r)

g = sp.diag(
    -sp.exp(2*A),          # g_tt
     sp.exp(2*B),          # g_rr
     r**2,                 # g_θθ
     r**2*sp.sin(theta)**2 # g_φφ
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

Riemann = [[[[None for _ in range(4)] for _ in range(4)]
            for _ in range(4)] for _ in range(4)]
for mu in range(4):
    for nu in range(4):
        for rho in range(4):
            for sigma in range(4):
                Riemann[mu][nu][rho][sigma] = Riemann_symbol(mu, nu, rho, sigma)

Ricci = [[None for _ in range(4)] for _ in range(4)]
for nu in range(4):
    for sigma in range(4):
        s = 0
        for mu in range(4):
            s += Riemann[mu][nu][mu][sigma]
        Ricci[nu][sigma] = sp.simplify(s)

R_tt = sp.simplify(Ricci[0][0])
R_rr = sp.simplify(Ricci[1][1])
R_tr = sp.simplify(Ricci[0][1])
R_thth = sp.simplify(Ricci[2][2])

print("R_tr (should vanish identically for static ansatz):")
print(R_tr)

print("\nR_tt =")
print(R_tt)

print("\nR_rr =")
print(R_rr)

print("\nR_θθ =")
print(R_thth)

# ----------------------------------------------------
# 2. Solve the vacuum equations by hand-ish, but guided by Sympy
#    We know vacuum: R_tt = R_rr = R_θθ = 0
#    Trick: use A(r) = -B(r), then solve R_θθ = 0 for B (or A).
# ----------------------------------------------------

# For this part, we define a new function f(r) = exp(-2B(r))
f = sp.Function('f')

# We want to re-express R_θθ in terms of f and its derivative.
# To do that, substitute exp(2*B) = 1/f(r).
B_r = sp.Function('B')(r)
A_r = -B_r  # gauge choice A = -B

R_thth_AB = R_thth.subs({A: A_r, B: B_r})

# Substitute exp(2B) = 1/f(r), exp(-2B) = f(r), and B' = -(f' / (2f))
fr = f(r)
fr_prime = sp.diff(fr, r)

subs_dict = {
    sp.exp(2*B_r): 1/fr,
    sp.exp(-2*B_r): fr,
    sp.diff(B_r, r): -(fr_prime/(2*fr))
}

R_thth_f = sp.simplify(R_thth_AB.subs(subs_dict))

print("\nR_θθ expressed in terms of f(r) and f'(r):")
print(R_thth_f)

# Now set R_θθ = 0 and simplify the resulting ODE for f(r):
ode = sp.simplify(sp.Eq(R_thth_f, 0))
print("\nODE from R_θθ = 0 (in terms of f and f'):")
print(ode)

# Manually, this ODE should boil down to: f'(r) = -(f(r) - 1)/r
# Solve that ODE directly:
f_symbol = sp.Function('f')
r_sym = r

ode_simple = sp.Eq(sp.diff(f_symbol(r_sym), r_sym), -(f_symbol(r_sym) - 1)/r_sym)
sol = sp.dsolve(ode_simple)
print("\nSolution of f'(r) = -(f-1)/r:")
print(sol)

# This gives f(r) = 1 + C/r. We rename the constant to -2M:
C1 = sp.symbols('C1')
f_solution = 1 + C1/r
print("\nf(r) = 1 + C1/r (rename C1 = -2M)")

# So e^{-2B} = f = 1 - 2M/r and e^{2A} = e^{-2B} -> Schwarzschild metric coefficients.
print("\nTherefore:")
print("e^{-2B(r)} = 1 - 2M/r")
print("e^{ 2A(r)} = 1 - 2M/r")

print("\nFinal Schwarzschild metric:")
print("ds^2 = -(1 - 2M/r) dt^2 + (1 - 2M/r)^{-1} dr^2 + r^2 (dθ^2 + sin^2θ dφ^2)")
