# Traffic Flow Modeling: jams, bottlenecks, and speed harmonization
# ---------------------------------------------------------------
# pip install numpy matplotlib
import numpy as np
import matplotlib.pyplot as plt

# ---------------- Core simulator (Nagel–Schreckenberg) ----------------
def simulate(L=300, density=0.18, vmax=5, p_slow=0.2, steps=2000, warmup=500,
             bottleneck=None, harmonize=None, seed=0):
    """
    L: road length (cells) on a ring; 1 cell ~ 7.5 m (optional mental model)
    density: cars / cell
    vmax: max speed (cells/step)
    p_slow: random slowdown prob everywhere (0..1)
    steps: total steps; warmup: ignore first steps for stats
    bottleneck: dict or None. If set, {'start':i0, 'end':i1, 'p_slow':pb} applies higher noise in [i0,i1)
    harmonize: dict or None. If set, {'start':j0, 'end':j1, 'vmax':vh} lowers vmax in [j0,j1) (speed harmonization)
    Returns: mean_flow (cars/step), time_space (array for plotting)
    """
    rng = np.random.default_rng(seed)
    N = int(round(density*L))
    # car positions (sorted) and speeds
    pos = np.sort(rng.choice(L, N, replace=False)).astype(int)
    v = np.zeros(N, dtype=int)

    # helpers
    def gap_ahead(i):
        # distance to next car (periodic)
        nxt = pos[(i+1) % N]
        g = (nxt - pos[i] - 1) % L
        return g

    flows = []
    record = np.full((steps - warmup, L), -1, dtype=int)  # -1 empty, else speed
    for t in range(steps):
        # 1) accelerate
        v = np.minimum(v + 1, vmax)

        # 2) slow to avoid collision
        gaps = np.array([gap_ahead(i) for i in range(N)])
        v = np.minimum(v, gaps)

        # 3) random slowdown (including bottleneck)
        if bottleneck:
            pb = bottleneck['p_slow']
            i0, i1 = bottleneck['start'] % L, bottleneck['end'] % L
            in_bneck = ( (pos >= i0) & (pos < i1) ) if i0 < i1 else ( (pos >= i0) | (pos < i1) )
        else:
            pb = None
            in_bneck = np.zeros(N, dtype=bool)

        # global randomization
        slow_mask = (v > 0) & (rng.random(N) < p_slow)
        v[slow_mask] -= 1

        # extra randomization inside bottleneck
        if pb is not None:
            slow_bn = (v > 0) & in_bneck & (rng.random(N) < (pb - p_slow))
            v[slow_bn] -= 1

        # 4) optional speed harmonization region with lower vmax
        if harmonize:
            vh = harmonize['vmax']
            j0, j1 = harmonize['start'] % L, harmonize['end'] % L
            in_harm = ( (pos >= j0) & (pos < j1) ) if j0 < j1 else ( (pos >= j0) | (pos < j1) )
            v[in_harm] = np.minimum(v[in_harm], vh)

        # move
        pos = (pos + v) % L

        # stats / record
        if t >= warmup:
            # flow = total distance advanced per step / road length
            flows.append(v.sum() / L)
            record[t - warmup, pos] = v  # mark current speeds

    return float(np.mean(flows)), record

# ---------------- Experiments that show usefulness ----------------
def fundamental_diagram():
    """Throughput vs density for baseline highway."""
    L = 300
    densities = np.linspace(0.02, 0.8, 30)
    flows = []
    for d in densities:
        f, _ = simulate(L=L, density=d, vmax=5, p_slow=0.2, steps=1500, warmup=300, seed=1)
        flows.append(f)
    plt.figure(figsize=(6,4))
    plt.plot(densities, flows, marker='o', lw=1.5)
    plt.xlabel('Density (cars per cell)')
    plt.ylabel('Flow (cars per timestep per cell)')
    plt.title('Fundamental Diagram (one-lane ring road)')
    plt.grid(True)
    plt.show()

def bottleneck_vs_harmonization():
    """
    Shows a common real situation: rubbernecking bottleneck (construction/accident)
    and a **gentle speed limit region** placed upstream to prevent stop-and-go waves.
    """
    L = 400
    density = 0.22             # moderately heavy traffic
    steps, warm = 2200, 500

    # Define a short bottleneck (more random braking over 40 cells)
    bn = {'start':220, 'end':260, 'p_slow':0.55}

    # Case A: bottleneck only
    flow_A, rec_A = simulate(L=L, density=density, vmax=5, p_slow=0.2,
                             steps=steps, warmup=warm, bottleneck=bn, harmonize=None, seed=2)

    # Case B: add **speed harmonization** (lower vmax to 3) 80 cells upstream over 80 cells
    harm = {'start':120, 'end':200, 'vmax':3}
    flow_B, rec_B = simulate(L=L, density=density, vmax=5, p_slow=0.2,
                             steps=steps, warmup=warm, bottleneck=bn, harmonize=harm, seed=2)

    print(f"Mean flow with bottleneck only:      {flow_A:.4f}")
    print(f"Mean flow with harmonization added: {flow_B:.4f}")

    # Visualize time–space diagrams (each row = time; white = higher speed, black = jam)
    fig, axs = plt.subplots(1,2, figsize=(11,4), sharey=True)
    im0 = axs[0].imshow(rec_A.T, aspect='auto', origin='lower', vmin=-1, vmax=5)
    axs[0].set_title('A) Bottleneck only (stop-and-go waves)')
    axs[0].set_xlabel('Time'); axs[0].set_ylabel('Position along road')

    im1 = axs[1].imshow(rec_B.T, aspect='auto', origin='lower', vmin=-1, vmax=5)
    axs[1].set_title('B) + Speed harmonization (smoother flow)')
    axs[1].set_xlabel('Time')
    cbar = fig.colorbar(im1, ax=axs.ravel().tolist(), shrink=0.9)
    cbar.set_label('Speed (cells/step), -1 = empty')
    plt.suptitle('Time–Space Diagrams: bright = fast, dark = jam')
    plt.tight_layout()
    plt.show()

# ---------------- Run the demo ----------------
if __name__ == "__main__":
    fundamental_diagram()
    bottleneck_vs_harmonization()
