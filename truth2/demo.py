#!/usr/bin/env python3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import statsmodels.api as sm
from sklearn.feature_selection import mutual_info_regression

np.random.seed(42)
n = 300

Z = np.random.normal(0, 1, n)
X = 0.8 * Z + np.random.normal(0, 1, n)
Y = 1.5 * X + 0.7 * Z + np.random.normal(0, 1, n)
W = np.random.normal(0, 1, n)
X_nl = np.random.normal(0, 1, n)
Y_nl = X_nl**2 + 0.3 * np.random.normal(0, 1, n)

df = pd.DataFrame({"X": X, "Y": Y, "Z": Z, "W": W, "X_nl": X_nl, "Y_nl": Y_nl})

def corr_with_p(a, b, method="pearson"):
    if method == "pearson":
        r, p = stats.pearsonr(a, b)
        return r, p
    elif method == "spearman":
        r, p = stats.spearmanr(a, b)
        return r, p
    elif method == "kendall":
        r, p = stats.kendalltau(a, b)
        return r, p
    else:
        raise ValueError("method must be pearson|spearman|kendall")

def residualize(target, covariates):
    Xmat = sm.add_constant(covariates)
    model = sm.OLS(target, Xmat).fit()
    return target - model.fittedvalues

def _centered_distance_matrix(x):
    x = np.atleast_2d(x).T
    a = np.abs(x - x.T)
    A = a - a.mean(axis=0) - a.mean(axis=1, keepdims=True) + a.mean()
    return A

def distance_correlation(x, y):
    A = _centered_distance_matrix(x)
    B = _centered_distance_matrix(y)
    dcov2_xy = (A * B).mean()
    dcov2_xx = (A * A).mean()
    dcov2_yy = (B * B).mean()
    if dcov2_xx <= 0 or dcov2_yy <= 0:
        return 0.0
    return np.sqrt(dcov2_xy / np.sqrt(dcov2_xx * dcov2_yy))

def partial_correlation_3var(df, var1, var2, control):
    """Compute partial correlation r_{var1,var2|control}"""
    r1 = residualize(df[var1], df[[control]])
    r2 = residualize(df[var2], df[[control]])
    r, p = stats.pearsonr(r1, r2)
    return r, p

def analyze_3_parameters(df, var1, var2, var3, target_var):
    """
    Comprehensive analysis of 3 parameters with respect to a target variable.
    Returns a dictionary with all relevant statistics and conclusions.
    """
    results = {}
    
    # 1. Zero-order correlations
    results['zero_order'] = {
        'r_1_target': corr_with_p(df[var1], df[target_var]),
        'r_2_target': corr_with_p(df[var2], df[target_var]),
        'r_3_target': corr_with_p(df[var3], df[target_var]),
        'r_12': corr_with_p(df[var1], df[var2]),
        'r_13': corr_with_p(df[var1], df[var3]),
        'r_23': corr_with_p(df[var2], df[var3]),
    }
    
    # 2. Partial correlations (controlling for each variable)
    results['partial_1_2_control3'] = partial_correlation_3var(df, var1, var2, var3)
    results['partial_1_3_control2'] = partial_correlation_3var(df, var1, var3, var2)
    results['partial_2_3_control1'] = partial_correlation_3var(df, var2, var3, var1)
    
    # Partial correlations with target
    results['partial_1_target_control2'] = partial_correlation_3var(df, var1, target_var, var2)
    results['partial_1_target_control3'] = partial_correlation_3var(df, var1, target_var, var3)
    results['partial_2_target_control1'] = partial_correlation_3var(df, var2, target_var, var1)
    results['partial_2_target_control3'] = partial_correlation_3var(df, var2, target_var, var3)
    results['partial_3_target_control1'] = partial_correlation_3var(df, var3, target_var, var1)
    results['partial_3_target_control2'] = partial_correlation_3var(df, var3, target_var, var2)
    
    # 3. Multiple regression with all 3 predictors
    X_all = sm.add_constant(df[[var1, var2, var3]])
    model_all = sm.OLS(df[target_var], X_all).fit()
    results['regression_all'] = {
        'model': model_all,
        'coef_1': (model_all.params[var1], model_all.pvalues[var1]),
        'coef_2': (model_all.params[var2], model_all.pvalues[var2]),
        'coef_3': (model_all.params[var3], model_all.pvalues[var3]),
        'r_squared': model_all.rsquared,
        'adj_r_squared': model_all.rsquared_adj,
        'f_statistic': (model_all.fvalue, model_all.f_pvalue),
    }
    
    # 4. Regression with interactions
    df_interact = df.copy()
    df_interact[f'{var1}x{var2}'] = df[var1] * df[var2]
    df_interact[f'{var1}x{var3}'] = df[var1] * df[var3]
    df_interact[f'{var2}x{var3}'] = df[var2] * df[var3]
    
    X_interact = sm.add_constant(df_interact[[var1, var2, var3, 
                                               f'{var1}x{var2}', 
                                               f'{var1}x{var3}', 
                                               f'{var2}x{var3}']])
    model_interact = sm.OLS(df[target_var], X_interact).fit()
    results['regression_interactions'] = {
        'model': model_interact,
        'interaction_12': (model_interact.params[f'{var1}x{var2}'], 
                          model_interact.pvalues[f'{var1}x{var2}']),
        'interaction_13': (model_interact.params[f'{var1}x{var3}'], 
                          model_interact.pvalues[f'{var1}x{var3}']),
        'interaction_23': (model_interact.params[f'{var2}x{var3}'], 
                          model_interact.pvalues[f'{var2}x{var3}']),
        'r_squared': model_interact.rsquared,
        'adj_r_squared': model_interact.rsquared_adj,
    }
    
    # 5. Mediation analysis (Sobel test)
    # Path a: X -> M
    # Path b: M -> Y (controlling for X)
    # We'll test if var2 mediates var1 -> target_var
    path_a_model = sm.OLS(df[var2], sm.add_constant(df[[var1]])).fit()
    path_b_model = sm.OLS(df[target_var], sm.add_constant(df[[var1, var2]])).fit()
    
    a = path_a_model.params[var1]
    b = path_b_model.params[var2]
    se_a = path_a_model.bse[var1]
    se_b = path_b_model.bse[var2]
    
    # Sobel test statistic
    sobel_stat = (a * b) / np.sqrt(b**2 * se_a**2 + a**2 * se_b**2)
    sobel_p = 2 * (1 - stats.norm.cdf(abs(sobel_stat)))
    
    results['mediation_2_mediates_1'] = {
        'indirect_effect': a * b,
        'sobel_statistic': sobel_stat,
        'sobel_pvalue': sobel_p,
        'path_a': (a, path_a_model.pvalues[var1]),
        'path_b': (b, path_b_model.pvalues[var2]),
    }
    
    return results

def generate_conclusions(results, var1, var2, var3, target_var):
    """Generate human-readable conclusions from 3-parameter analysis"""
    conclusions = []
    
    # Zero-order correlations
    r1t, p1t = results['zero_order']['r_1_target']
    r2t, p2t = results['zero_order']['r_2_target']
    r3t, p3t = results['zero_order']['r_3_target']
    
    conclusions.append(f"\n=== RELATIONSHIPS WITH TARGET ({target_var}) ===")
    conclusions.append(f"{var1} -> {target_var}: r={r1t:.3f}, p={p1t:.4f} {'***' if p1t<0.001 else '**' if p1t<0.01 else '*' if p1t<0.05 else 'ns'}")
    conclusions.append(f"{var2} -> {target_var}: r={r2t:.3f}, p={p2t:.4f} {'***' if p2t<0.001 else '**' if p2t<0.01 else '*' if p2t<0.05 else 'ns'}")
    conclusions.append(f"{var3} -> {target_var}: r={r3t:.3f}, p={p3t:.4f} {'***' if p3t<0.001 else '**' if p3t<0.01 else '*' if p3t<0.05 else 'ns'}")
    
    # Partial correlations
    conclusions.append(f"\n=== PARTIAL CORRELATIONS (CONTROLLING FOR CONFOUNDERS) ===")
    r1t_c2, p1t_c2 = results['partial_1_target_control2']
    r1t_c3, p1t_c3 = results['partial_1_target_control3']
    r2t_c1, p2t_c1 = results['partial_2_target_control1']
    r2t_c3, p2t_c3 = results['partial_2_target_control3']
    r3t_c1, p3t_c1 = results['partial_3_target_control1']
    r3t_c2, p3t_c2 = results['partial_3_target_control2']
    
    conclusions.append(f"{var1} -> {target_var} | {var2}: r={r1t_c2:.3f}, p={p1t_c2:.4f}")
    conclusions.append(f"{var1} -> {target_var} | {var3}: r={r1t_c3:.3f}, p={p1t_c3:.4f}")
    conclusions.append(f"{var2} -> {target_var} | {var1}: r={r2t_c1:.3f}, p={p2t_c1:.4f}")
    conclusions.append(f"{var2} -> {target_var} | {var3}: r={r2t_c3:.3f}, p={p2t_c3:.4f}")
    conclusions.append(f"{var3} -> {target_var} | {var1}: r={r3t_c1:.3f}, p={p3t_c1:.4f}")
    conclusions.append(f"{var3} -> {target_var} | {var2}: r={r3t_c2:.3f}, p={p3t_c2:.4f}")
    
    # Multiple regression
    reg_all = results['regression_all']
    conclusions.append(f"\n=== MULTIPLE REGRESSION: {target_var} ~ {var1} + {var2} + {var3} ===")
    conclusions.append(f"R-squared: {reg_all['r_squared']:.4f}, Adj R-squared: {reg_all['adj_r_squared']:.4f}")
    coef1, p1 = reg_all['coef_1']
    coef2, p2 = reg_all['coef_2']
    coef3, p3 = reg_all['coef_3']
    conclusions.append(f"{var1} coefficient: {coef1:.4f}, p={p1:.4f} {'***' if p1<0.001 else '**' if p1<0.01 else '*' if p1<0.05 else 'ns'}")
    conclusions.append(f"{var2} coefficient: {coef2:.4f}, p={p2:.4f} {'***' if p2<0.001 else '**' if p2<0.01 else '*' if p2<0.05 else 'ns'}")
    conclusions.append(f"{var3} coefficient: {coef3:.4f}, p={p3:.4f} {'***' if p3<0.001 else '**' if p3<0.01 else '*' if p3<0.05 else 'ns'}")
    
    # Interactions
    reg_int = results['regression_interactions']
    conclusions.append(f"\n=== INTERACTION EFFECTS ===")
    int12_coef, int12_p = reg_int['interaction_12']
    int13_coef, int13_p = reg_int['interaction_13']
    int23_coef, int23_p = reg_int['interaction_23']
    conclusions.append(f"{var1} x {var2}: coef={int12_coef:.4f}, p={int12_p:.4f} {'***' if int12_p<0.001 else '**' if int12_p<0.01 else '*' if int12_p<0.05 else 'ns'}")
    conclusions.append(f"{var1} x {var3}: coef={int13_coef:.4f}, p={int13_p:.4f} {'***' if int13_p<0.001 else '**' if int13_p<0.01 else '*' if int13_p<0.05 else 'ns'}")
    conclusions.append(f"{var2} x {var3}: coef={int23_coef:.4f}, p={int23_p:.4f} {'***' if int23_p<0.001 else '**' if int23_p<0.01 else '*' if int23_p<0.05 else 'ns'}")
    
    # Mediation
    med = results['mediation_2_mediates_1']
    conclusions.append(f"\n=== MEDIATION ANALYSIS ({var2} mediates {var1} -> {target_var}) ===")
    conclusions.append(f"Indirect effect: {med['indirect_effect']:.4f}")
    conclusions.append(f"Sobel test: z={med['sobel_statistic']:.3f}, p={med['sobel_pvalue']:.4f}")
    if med['sobel_pvalue'] < 0.05:
        conclusions.append(f"CONCLUSION: {var2} significantly mediates the relationship between {var1} and {target_var}")
    else:
        conclusions.append(f"CONCLUSION: No significant mediation effect detected")
    
    # Overall conclusions
    conclusions.append(f"\n=== KEY CONCLUSIONS ===")
    strongest = max([(r1t, var1), (r2t, var2), (r3t, var3)], key=lambda x: abs(x[0]))
    conclusions.append(f"Strongest predictor: {strongest[1]} (r={strongest[0]:.3f})")
    
    if reg_all['r_squared'] > 0.5:
        conclusions.append(f"Model explains {reg_all['r_squared']*100:.1f}% of variance - GOOD fit")
    elif reg_all['r_squared'] > 0.3:
        conclusions.append(f"Model explains {reg_all['r_squared']*100:.1f}% of variance - MODERATE fit")
    else:
        conclusions.append(f"Model explains {reg_all['r_squared']*100:.1f}% of variance - WEAK fit")
    
    significant_vars = []
    if p1 < 0.05: significant_vars.append(var1)
    if p2 < 0.05: significant_vars.append(var2)
    if p3 < 0.05: significant_vars.append(var3)
    
    if len(significant_vars) > 0:
        conclusions.append(f"Significant independent predictors: {', '.join(significant_vars)}")
    else:
        conclusions.append("No significant independent predictors found")
    
    return "\n".join(conclusions)

# 1) Classic correlations
pairs = {
    "X vs Y (linear/confounded)": ("X", "Y"),
    "X vs W (independent)": ("X", "W"),
    "X_nl vs Y_nl (nonlinear)": ("X_nl", "Y_nl"),
}

rows = []
for label, (a, b) in pairs.items():
    pearson_r, pearson_p = corr_with_p(df[a], df[b], "pearson")
    spearman_r, spearman_p = corr_with_p(df[a], df[b], "spearman")
    kendall_r, kendall_p = corr_with_p(df[a], df[b], "kendall")
    rows.append([label, pearson_r, pearson_p, spearman_r, spearman_p, kendall_r, kendall_p])

corr_table = pd.DataFrame(rows, columns=[
    "Pair", "Pearson r", "Pearson p", "Spearman rho", "Spearman p", "Kendall tau", "Kendall p"
])

# 2) Partial correlation r_{XY·Z}
rx = residualize(df["X"], df[["Z"]])
ry = residualize(df["Y"], df[["Z"]])
partial_r, partial_p = stats.pearsonr(rx, ry)

# 3) OLS and Robust regression
Xmat = sm.add_constant(df[["X", "Z"]])
ols_model = sm.OLS(df["Y"], Xmat).fit()
rlm_model = sm.RLM(df["Y"], Xmat, M=sm.robust.norms.HuberT()).fit()

# 4) Nonlinear detection
dcor_linear = distance_correlation(df["X"].values, df["Y"].values)
dcor_nonlinear = distance_correlation(df["X_nl"].values, df["Y_nl"].values)
mi_linear = mutual_info_regression(df[["X"]], df["Y"], random_state=42)[0]
mi_nonlinear = mutual_info_regression(df[["X_nl"]], df["Y_nl"], random_state=42)[0]

nonlin_table = pd.DataFrame({
    "Pair": ["X vs Y (linear/confounded)", "X_nl vs Y_nl (nonlinear)"],
    "Distance corr": [dcor_linear, dcor_nonlinear],
    "Mutual information": [mi_linear, mi_nonlinear]
})

print("=== Classic correlations ===")
print(corr_table.round(4).to_string(index=False))
print("\n=== Partial correlation r_{XY·Z} (control Z) ===")
print(f"Partial Pearson r (X, Y | Z): {partial_r:.4f}, p-value: {partial_p:.4g}")
print("\n=== OLS regression: Y ~ X + Z ===")
print(ols_model.summary())
print("\n=== Robust regression (Huber): Y ~ X + Z ===")
print(rlm_model.summary())
print("\n=== Nonlinear detection ===")
print(nonlin_table.round(4).to_string(index=False))

# ===== 3-PARAMETER ANALYSIS =====
print("\n" + "="*80)
print("3-PARAMETER COMPREHENSIVE ANALYSIS")
print("="*80)

# Analyze X, Z, W as predictors of Y
results_3param = analyze_3_parameters(df, "X", "Z", "W", "Y")

# Create summary table
summary_rows = []
zero = results_3param['zero_order']
reg = results_3param['regression_all']
reg_int = results_3param['regression_interactions']

summary_rows.append({
    "Variable": "X",
    "Zero-order r": f"{zero['r_1_target'][0]:.4f}",
    "Zero-order p": f"{zero['r_1_target'][1]:.4g}",
    "Partial r (|Z)": f"{results_3param['partial_1_target_control2'][0]:.4f}",
    "Partial r (|W)": f"{results_3param['partial_1_target_control3'][0]:.4f}",
    "Reg coef": f"{reg['coef_1'][0]:.4f}",
    "Reg p": f"{reg['coef_1'][1]:.4g}",
})

summary_rows.append({
    "Variable": "Z",
    "Zero-order r": f"{zero['r_2_target'][0]:.4f}",
    "Zero-order p": f"{zero['r_2_target'][1]:.4g}",
    "Partial r (|X)": f"{results_3param['partial_2_target_control1'][0]:.4f}",
    "Partial r (|W)": f"{results_3param['partial_2_target_control3'][0]:.4f}",
    "Reg coef": f"{reg['coef_2'][0]:.4f}",
    "Reg p": f"{reg['coef_2'][1]:.4g}",
})

summary_rows.append({
    "Variable": "W",
    "Zero-order r": f"{zero['r_3_target'][0]:.4f}",
    "Zero-order p": f"{zero['r_3_target'][1]:.4g}",
    "Partial r (|X)": f"{results_3param['partial_3_target_control1'][0]:.4f}",
    "Partial r (|Z)": f"{results_3param['partial_3_target_control2'][0]:.4f}",
    "Reg coef": f"{reg['coef_3'][0]:.4f}",
    "Reg p": f"{reg['coef_3'][1]:.4g}",
})

summary_table = pd.DataFrame(summary_rows)
print("\n=== SUMMARY TABLE: 3-PARAMETER ANALYSIS (X, Z, W -> Y) ===")
print(summary_table.to_string(index=False))

# Print detailed conclusions
conclusions = generate_conclusions(results_3param, "X", "Z", "W", "Y")
print(conclusions)

# Print full regression models
print("\n=== FULL MULTIPLE REGRESSION MODEL ===")
print(results_3param['regression_all']['model'].summary())

print("\n=== REGRESSION WITH INTERACTIONS ===")
print(results_3param['regression_interactions']['model'].summary())

# Plots
fig = plt.figure(figsize=(15, 10))

# Original plots
ax1 = plt.subplot(2, 3, 1)
coef = np.polyfit(df['X'], df['Y'], 1)
xline = np.linspace(df['X'].min(), df['X'].max(), 200)
yline = coef[0]*xline + coef[1]
ax1.scatter(df['X'], df['Y'], alpha=0.6)
ax1.plot(xline, yline, 'r-', linewidth=2)
ax1.set_title("X vs Y (linear/confounded)")
ax1.set_xlabel("X"); ax1.set_ylabel("Y")

ax2 = plt.subplot(2, 3, 2)
coef_w = np.polyfit(df['X'], df['W'], 1)
xline_w = np.linspace(df['X'].min(), df['X'].max(), 200)
yline_w = coef_w[0]*xline_w + coef_w[1]
ax2.scatter(df['X'], df['W'], alpha=0.6)
ax2.plot(xline_w, yline_w, 'r-', linewidth=2)
ax2.set_title("X vs W (independent)")
ax2.set_xlabel("X"); ax2.set_ylabel("W")

ax3 = plt.subplot(2, 3, 3)
coef2 = np.polyfit(df['X_nl'], df['Y_nl'], 2)
xline2 = np.linspace(df['X_nl'].min(), df['X_nl'].max(), 200)
yline2 = coef2[0]*xline2**2 + coef2[1]*xline2 + coef2[2]
ax3.scatter(df['X_nl'], df['Y_nl'], alpha=0.6)
ax3.plot(xline2, yline2, 'r-', linewidth=2)
ax3.set_title("X_nl vs Y_nl (nonlinear)")
ax3.set_xlabel("X_nl"); ax3.set_ylabel("Y_nl")

# 3-parameter analysis plots
ax4 = plt.subplot(2, 3, 4)
ax4.scatter(df['X'], df['Y'], alpha=0.5, label='X vs Y', s=30)
ax4.scatter(df['Z'], df['Y'], alpha=0.5, label='Z vs Y', s=30)
ax4.set_xlabel("Predictors"); ax4.set_ylabel("Y")
ax4.set_title("3-Parameter: X, Z vs Y")
ax4.legend()

ax5 = plt.subplot(2, 3, 5)
# Residual plot for X controlling for Z
rx_resid = residualize(df["X"], df[["Z"]])
ry_resid = residualize(df["Y"], df[["Z"]])
ax5.scatter(rx_resid, ry_resid, alpha=0.6)
coef_resid = np.polyfit(rx_resid, ry_resid, 1)
xline_resid = np.linspace(rx_resid.min(), rx_resid.max(), 200)
yline_resid = coef_resid[0]*xline_resid + coef_resid[1]
ax5.plot(xline_resid, yline_resid, 'r-', linewidth=2)
ax5.set_title("Partial: X vs Y | Z")
ax5.set_xlabel("X (residualized)"); ax5.set_ylabel("Y (residualized)")

ax6 = plt.subplot(2, 3, 6)
# 3D-like visualization: color by third variable
scatter = ax6.scatter(df['X'], df['Z'], c=df['Y'], cmap='viridis', alpha=0.6, s=50)
ax6.set_xlabel("X"); ax6.set_ylabel("Z")
ax6.set_title("X vs Z (colored by Y)")
plt.colorbar(scatter, ax=ax6, label='Y')

plt.tight_layout()
plt.show()
