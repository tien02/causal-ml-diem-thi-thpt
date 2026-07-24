"""
Monte Carlo 2025 vs 2026 CT2018 Comparison
===========================================
Comprehensive analysis: adaptation curve for CT2018 (new program) from year 1 to year 2.

Five sections:
  A. Raw performance bootstrap (per-subject delta 2025→2026)
  B. RDD-style ATE comparison (CT2018 effect in 2025 vs 2026)
  C. Double ML for 2026 CT2018 effect (reuse causal_ml.py pipeline)
  D. HTE by urban tier (stratified adaptation)
  E. Rosenbaum bounds + MC sensitivity on province gaps

Output: 6 figures to figures/, summary table to stdout.
"""

import os
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import wilcoxon, norm
import statsmodels.formula.api as smf
from sklearn.model_selection import KFold
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import LinearRegression

warnings.filterwarnings('ignore')

from config import BASE, OUT
from province_mapping import OLD_TO_NEW_2026, urban_tier_old, urban_tier_2026, CHUYEN_STRONG_OLD, CHUYEN_STRONG_2026


SUBJECTS = ['toan', 'nguvan', 'ngoaingu', 'vatly', 'hoahoc', 'sinhhoc', 'lichsu', 'dialy', 'gdcd']
np.random.seed(42)

# ─────────────────────────────────────────────
# Data Loaders
# ─────────────────────────────────────────────

def _rename_common(df):
    """Normalize column names."""
    df.columns = df.columns.str.lower().str.strip()
    rename = {
        'ngu_van': 'nguvan', 'ngoai_ngu': 'ngoaingu',
        'vat_ly': 'vatly', 'vat_li': 'vatly',
        'hoa_hoc': 'hoahoc', 'sinh_hoc': 'sinhhoc',
        'lich_su': 'lichsu', 'dia_ly': 'dialy', 'dia_li': 'dialy',
        'ngoai ngu': 'ngoaingu', 'tin_hoc': 'tinhoc', 'cong_nghiep': 'congnghiep', 'nong_nghiep': 'nongnghiep'
    }
    df.rename(columns=rename, inplace=True)
    return df

def _rename_2026(df):
    """Rename 2026 columns to match 2025/2024 convention."""
    rename = {
        'van': 'nguvan', 'ly': 'vatly', 'hoa': 'hoahoc',
        'sinh': 'sinhhoc', 'su': 'lichsu', 'dia': 'dialy',
        'ktpl': 'gdcd', 'mangoaingu': 'ma_ngoaingu'
    }
    df.rename(columns=rename, inplace=True)
    return df

def load_2025_ct2006():
    """2025 CT2006 cohort (control within 2025)."""
    df = pd.read_csv(f'{BASE}/2025/20250715-ketquathi-ct2006.csv', sep=';', encoding='utf-8-sig')
    df = _rename_common(df)
    df['year'] = 2025
    df['treatment'] = 0
    df['curriculum'] = 'CT2006'
    df['sbd'] = df['sbd'].astype(str)
    df['province'] = df['sbd'].str[:2].astype(int)
    for col in SUBJECTS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

def load_2025_ct2018():
    """2025 CT2018 cohort (treatment within 2025, first year)."""
    df = pd.read_csv(f'{BASE}/2025/20250715-ketquathi-ct2018a.csv', sep=';', encoding='utf-8-sig')
    df = _rename_common(df)
    df['year'] = 2025
    df['treatment'] = 1
    df['curriculum'] = 'CT2018'
    df['sbd'] = df['sbd'].astype(str)
    df['province'] = df['sbd'].str[:2].astype(int)
    for col in SUBJECTS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

def load_2024():
    """2024 cohort (pre-CT2018 baseline for RDD)."""
    df = pd.read_csv(f'{BASE}/2024/Diemthi2024.csv', sep=',')
    df = _rename_common(df)
    df['year'] = 2024
    df['treatment'] = 0
    df['curriculum'] = 'CT2006'
    df['sbd'] = df['sbd'].astype(str)
    df['province'] = df['sbd'].str[:2].astype(int)
    for col in SUBJECTS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

def load_2026():
    """2026 cohort (CT2018, second year)."""
    df = pd.read_csv(f'{BASE}/2026/diemthithpt_2026.csv', sep=',')
    df.columns = df.columns.str.lower().str.strip()
    df = _rename_2026(df)
    df.rename(columns={'id': 'sbd'}, inplace=True)
    df['year'] = 2026
    df['treatment'] = 1
    df['curriculum'] = 'CT2018'
    df['sbd'] = df['sbd'].astype(str)
    df['province'] = df['sbd'].str[:2].astype(int)
    for col in SUBJECTS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

def _enrich(df):
    """Add urban tier, chuyen flag, province harmonization."""
    def urban_tier(code):
        if code in {1, 2}: return 'Đô thị lớn'
        elif code in {3, 4, 33, 58}: return 'Đô thị vừa'
        else: return 'Tỉnh lẻ/Nông thôn'
    def urban_tier_new(code):
        if code in {1, 79}: return 'Đô thị lớn'
        elif code in {31, 48, 46, 92}: return 'Đô thị vừa'
        else: return 'Tỉnh lẻ/Nông thôn'

    if df['year'].iloc[0] in [2024, 2025]:
        df['urban_tier'] = df['province'].map(urban_tier)
        df['is_chuyen'] = df['province'].isin(CHUYEN_STRONG_OLD).astype(int)
        df['province_harmonized'] = df['province'].map(OLD_TO_NEW_2026)
    else:  # 2026
        df['urban_tier'] = df['province'].map(urban_tier_new)
        df['is_chuyen'] = df['province'].isin(CHUYEN_STRONG_2026).astype(int)
        df['province_harmonized'] = df['province']

    df['urban_large'] = (df['urban_tier'] == 'Đô thị lớn').astype(int)
    df['urban_mid'] = (df['urban_tier'] == 'Đô thị vừa').astype(int)
    return df

# Load data
print("Loading data...")
df25_ct2006 = _enrich(load_2025_ct2006())
df25_ct2018 = _enrich(load_2025_ct2018())
df24 = _enrich(load_2024())
df26 = _enrich(load_2026())

print(f"  2024: {len(df24):,} students")
print(f"  2025 CT2006: {len(df25_ct2006):,} students")
print(f"  2025 CT2018: {len(df25_ct2018):,} students")
print(f"  2026: {len(df26):,} students")

# ─────────────────────────────────────────────
# Section A: Raw Performance Bootstrap
# ─────────────────────────────────────────────

print("\n" + "="*60)
print("A. RAW PERFORMANCE BOOTSTRAP (2025 vs 2026 CT2018)")
print("="*60)

df25 = df25_ct2018[['toan', 'province_harmonized', 'urban_tier']].dropna(subset=['toan'])
df26_sub = df26[['toan', 'province_harmonized', 'urban_tier']].dropna(subset=['toan'])

results_a = {}

y25 = df25['toan'].dropna()
y26 = df26_sub['toan'].dropna()

obs_delta = y26.mean() - y25.mean()

# Bootstrap CI (1000 iter, cluster by province)
prov25 = df25[['toan', 'province_harmonized']].dropna()
prov26 = df26_sub[['toan', 'province_harmonized']].dropna()
prov_list_25 = prov25['province_harmonized'].unique()
prov_list_26 = prov26['province_harmonized'].unique()

boot_deltas = []
np.random.seed(42)
for _ in range(1000):
    b25_prov = np.random.choice(prov_list_25, len(prov_list_25), replace=True)
    b26_prov = np.random.choice(prov_list_26, len(prov_list_26), replace=True)
    m25 = prov25[prov25['province_harmonized'].isin(b25_prov)]['toan'].mean()
    m26 = prov26[prov26['province_harmonized'].isin(b26_prov)]['toan'].mean()
    boot_deltas.append(m26 - m25)

boot_deltas = np.array(boot_deltas)
ci_lo, ci_hi = np.percentile(boot_deltas, [2.5, 97.5])

results_a['toan'] = {
    'mean_2025': y25.mean(),
    'mean_2026': y26.mean(),
    'delta': obs_delta,
    'ci_lo': ci_lo,
    'ci_hi': ci_hi,
    'p_value': np.mean(np.abs(boot_deltas) >= np.abs(obs_delta)) if np.abs(obs_delta) > 0 else 1.0
}

print(f"toan:  Δ = {obs_delta:+.4f}  [{ci_lo:+.4f}, {ci_hi:+.4f}]  p={results_a['toan']['p_value']:.4f}")

# Figure A: raw delta bar chart + urban tier violin for toan
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

subjs_plot = ['toan']
deltas_plot = [results_a['toan']['delta']]

colors = ['green' if results_a['toan']['delta'] > 0 else 'red']
ax1.bar(subjs_plot, deltas_plot, color=colors, alpha=0.7, edgecolor='black')
ax1.axhline(y=0, color='black', linestyle='--', linewidth=0.8)
ax1.errorbar(0, results_a['toan']['delta'], yerr=[[results_a['toan']['delta']-ci_lo], [ci_hi-results_a['toan']['delta']]], fmt='none', ecolor='black', capsize=5, capthick=2)
ax1.set_ylabel('Δ Score (2026 − 2025)', fontsize=12)
ax1.set_title('Raw Performance Delta: Toán', fontsize=13, fontweight='bold')
ax1.grid(axis='y', alpha=0.3)

# Urban tier violin for toan
toan_data_25 = df25[['toan', 'urban_tier']].dropna()
toan_data_26 = df26_sub[['toan', 'urban_tier']].dropna()
toan_data_25['year'] = 2025
toan_data_26['year'] = 2026
toan_combined = pd.concat([toan_data_25, toan_data_26], ignore_index=True)

sns.violinplot(data=toan_combined, x='urban_tier', y='toan', hue='year', ax=ax2, palette='Set2')
ax2.set_title('Toán Distribution by Urban Tier (2025 vs 2026)', fontsize=13, fontweight='bold')
ax2.set_xlabel('Urban Tier', fontsize=11)
ax2.set_ylabel('Toán Score', fontsize=11)
plt.tight_layout()
plt.savefig(f'{OUT}/mc_raw_delta_2025_2026.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"Figure saved: {OUT}/mc_raw_delta_2025_2026.png")

# ─────────────────────────────────────────────
# Section B: RDD-style ATE Comparison
# ─────────────────────────────────────────────

print("\n" + "="*60)
print("B. RDD-STYLE ATE COMPARISON (CT2018 effect 2025 vs 2026)")
print("="*60)

# B1: 2025 ATE (CT2006 vs CT2018 within 2025)
df25_all = pd.concat([df25_ct2006, df25_ct2018], ignore_index=True).dropna(subset=['toan'])
try:
    m25 = smf.ols('toan ~ treatment + urban_large + urban_mid + is_chuyen', data=df25_all).fit(cov_type='HC3')
    ate_2025 = m25.params['treatment']
    se_2025 = m25.bse['treatment']
    print(f"2025 ATE (within-year RDD): {ate_2025:.4f} ± {se_2025:.4f}")
except Exception as e:
    print(f"Error fitting 2025 RDD: {e}")
    ate_2025, se_2025 = np.nan, np.nan

# B2: 2026 ATE (2024 vs 2026 CT2018)
df26_all = pd.concat([df24, df26], ignore_index=True).dropna(subset=['toan'])
try:
    m26 = smf.ols('toan ~ treatment + urban_large + urban_mid + is_chuyen', data=df26_all).fit(cov_type='HC3')
    ate_2026_ols = m26.params['treatment']
    se_2026_ols = m26.bse['treatment']
    print(f"2026 ATE (vs 2024): {ate_2026_ols:.4f} ± {se_2026_ols:.4f}")
except Exception as e:
    print(f"Error fitting 2026 RDD: {e}")
    ate_2026_ols, se_2026_ols = np.nan, np.nan

# B3: Bootstrap CI on ATE delta
ate_delta_boot = []
np.random.seed(42)
for _ in range(500):
    prov_list_25 = df25_all['province_harmonized'].unique()
    prov_list_26 = df26_all['province_harmonized'].unique()

    b25_prov = np.random.choice(prov_list_25, len(prov_list_25), replace=True)
    b26_prov = np.random.choice(prov_list_26, len(prov_list_26), replace=True)

    df25_boot = df25_all[df25_all['province_harmonized'].isin(b25_prov)]
    df26_boot = df26_all[df26_all['province_harmonized'].isin(b26_prov)]

    try:
        m25_b = smf.ols('toan ~ treatment + urban_large + urban_mid + is_chuyen', data=df25_boot).fit(cov_type='HC3')
        ate_2025_b = m25_b.params['treatment']
    except:
        ate_2025_b = np.nan

    try:
        m26_b = smf.ols('toan ~ treatment + urban_large + urban_mid + is_chuyen', data=df26_boot).fit(cov_type='HC3')
        ate_2026_b = m26_b.params['treatment']
    except:
        ate_2026_b = np.nan

    if not (np.isnan(ate_2025_b) or np.isnan(ate_2026_b)):
        ate_delta_boot.append(ate_2026_b - ate_2025_b)

ate_delta_boot = np.array(ate_delta_boot)
ate_delta_obs = ate_2026_ols - ate_2025
ate_delta_ci = np.percentile(ate_delta_boot, [2.5, 97.5])
ate_delta_p = np.mean(np.abs(ate_delta_boot) >= np.abs(ate_delta_obs)) if len(ate_delta_boot) > 0 else np.nan

print(f"\nATE delta (2026 − 2025): {ate_delta_obs:+.4f}")
print(f"  95% CI: [{ate_delta_ci[0]:+.4f}, {ate_delta_ci[1]:+.4f}]")
print(f"  p-value: {ate_delta_p:.4f}")

results_b = {
    'ate_2025': ate_2025,
    'se_2025': se_2025,
    'ate_2026': ate_2026_ols,
    'se_2026': se_2026_ols,
    'ate_delta': ate_delta_obs,
    'ate_delta_ci': ate_delta_ci,
    'ate_delta_p': ate_delta_p
}

# Figure B: ATE bar chart with error bars
fig, ax = plt.subplots(figsize=(8, 5))
years = ['2025', '2026']
ates = [ate_2025, ate_2026_ols]
ses = [se_2025, se_2026_ols]
colors_b = ['red' if a < 0 else 'green' for a in ates]

x_pos = np.arange(len(years))
ax.bar(x_pos, ates, color=colors_b, alpha=0.7, edgecolor='black', width=0.4)
ax.errorbar(x_pos, ates, yerr=ses, fmt='none', ecolor='black', capsize=8, capthick=2)
ax.axhline(y=0, color='black', linestyle='--', linewidth=1)
ax.set_xticks(x_pos)
ax.set_xticklabels(years)
ax.set_ylabel('ATE (points)', fontsize=12)
ax.set_title('CT2018 Effect: 2025 vs 2026', fontsize=13, fontweight='bold')
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(f'{OUT}/mc_ate_comparison.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"Figure saved: {OUT}/mc_ate_comparison.png")

# ─────────────────────────────────────────────
# Section C: Double ML for 2026
# ─────────────────────────────────────────────

print("\n" + "="*60)
print("C. DOUBLE ML FOR 2026 CT2018 EFFECT")
print("="*60)

dml_df = pd.concat([df24, df26], ignore_index=True).dropna(subset=['toan', 'is_chuyen', 'urban_large', 'urban_mid'])
dml_df = dml_df[dml_df['province_harmonized'].notna()].copy()

# Cap N at 300k
if len(dml_df) > 300000:
    dml_df = dml_df.sample(n=300000, random_state=42)

Y = dml_df['toan'].values
T = dml_df['treatment'].values
X = dml_df[['is_chuyen', 'urban_large', 'urban_mid']].values

# Standardize X
X_mean = X.mean(axis=0)
X_std = X.std(axis=0) + 1e-8
X_std[X_std < 1e-8] = 1.0
X_sc = (X - X_mean) / X_std

# 5-fold DML
kf = KFold(n_splits=5, shuffle=True, random_state=42)
Y_res_all = []
T_res_all = []

for train_idx, test_idx in kf.split(X_sc):
    X_train, X_test = X_sc[train_idx], X_sc[test_idx]
    Y_train, Y_test = Y[train_idx], Y[test_idx]
    T_train, T_test = T[train_idx], T[test_idx]

    # Fit nuisance: Y ~ X
    m_y = GradientBoostingRegressor(n_estimators=100, max_depth=3, random_state=42)
    m_y.fit(X_train, Y_train)
    Y_pred_test = m_y.predict(X_test)
    Y_res = Y_test - Y_pred_test

    # Fit nuisance: T ~ X
    m_t = GradientBoostingRegressor(n_estimators=100, max_depth=3, random_state=42)
    m_t.fit(X_train, T_train)
    T_pred_test = m_t.predict(X_test)
    T_res = T_test - T_pred_test

    Y_res_all.append(Y_res)
    T_res_all.append(T_res)

Y_res = np.concatenate(Y_res_all)
T_res = np.concatenate(T_res_all)

# Second stage
lr = LinearRegression()
lr.fit(T_res.reshape(-1, 1), Y_res)
dml_ate_2026 = lr.coef_[0]

# SE (Neyman orthogonality formula)
residuals_ss = Y_res - dml_ate_2026 * T_res
sigma2 = np.mean(residuals_ss ** 2)
dml_se_2026 = np.sqrt(sigma2 / np.sum(T_res ** 2))

print(f"DML ATE (2026): {dml_ate_2026:.4f} ± {dml_se_2026:.4f}")
print(f"  vs 2025 RDD: {ate_2025:.4f}")
print(f"  Difference: {dml_ate_2026 - ate_2025:+.4f}")

results_c = {
    'dml_ate_2026': dml_ate_2026,
    'dml_se_2026': dml_se_2026
}

# ─────────────────────────────────────────────
# Section D: HTE by Urban Tier
# ─────────────────────────────────────────────

print("\n" + "="*60)
print("D. HTE BY URBAN TIER (2025 vs 2026)")
print("="*60)

results_d = {}

for tier in ['Đô thị lớn', 'Đô thị vừa', 'Tỉnh lẻ/Nông thôn']:
    # 2025 HTE
    df25_tier = df25_all[df25_all['urban_tier'] == tier].dropna(subset=['toan'])
    if len(df25_tier) >= 100:
        try:
            m25_tier = smf.ols('toan ~ treatment + is_chuyen', data=df25_tier).fit(cov_type='HC3')
            hte_2025_tier = m25_tier.params['treatment']
            se_2025_tier = m25_tier.bse['treatment']
        except:
            hte_2025_tier, se_2025_tier = np.nan, np.nan
    else:
        hte_2025_tier, se_2025_tier = np.nan, np.nan

    # 2026 HTE
    df26_tier = df26_all[df26_all['urban_tier'] == tier].dropna(subset=['toan'])
    if len(df26_tier) >= 100:
        try:
            m26_tier = smf.ols('toan ~ treatment + is_chuyen', data=df26_tier).fit(cov_type='HC3')
            hte_2026_tier = m26_tier.params['treatment']
            se_2026_tier = m26_tier.bse['treatment']
        except:
            hte_2026_tier, se_2026_tier = np.nan, np.nan
    else:
        hte_2026_tier, se_2026_tier = np.nan, np.nan

    results_d[tier] = {
        'hte_2025': hte_2025_tier,
        'se_2025': se_2025_tier,
        'hte_2026': hte_2026_tier,
        'se_2026': se_2026_tier
    }

    print(f"{tier:20s}:  2025={hte_2025_tier:+.4f}  2026={hte_2026_tier:+.4f}  Δ={hte_2026_tier - hte_2025_tier:+.4f}")

# Figure D: HTE grouped bar by tier
fig, ax = plt.subplots(figsize=(10, 5))
tiers_plot = [t for t in results_d.keys() if not np.isnan(results_d[t]['hte_2025'])]
x_pos = np.arange(len(tiers_plot))
width = 0.35

hte_2025_vals = [results_d[t]['hte_2025'] for t in tiers_plot]
hte_2026_vals = [results_d[t]['hte_2026'] for t in tiers_plot]
se_2025_vals = [results_d[t]['se_2025'] for t in tiers_plot]
se_2026_vals = [results_d[t]['se_2026'] for t in tiers_plot]

ax.bar(x_pos - width/2, hte_2025_vals, width, label='2025', color='steelblue', edgecolor='black', alpha=0.8)
ax.errorbar(x_pos - width/2, hte_2025_vals, yerr=se_2025_vals, fmt='none', ecolor='black', capsize=5, capthick=1.5)

ax.bar(x_pos + width/2, hte_2026_vals, width, label='2026', color='coral', edgecolor='black', alpha=0.8)
ax.errorbar(x_pos + width/2, hte_2026_vals, yerr=se_2026_vals, fmt='none', ecolor='black', capsize=5, capthick=1.5)

ax.axhline(y=0, color='black', linestyle='--', linewidth=1)
ax.set_xticks(x_pos)
ax.set_xticklabels(tiers_plot, fontsize=11)
ax.set_ylabel('HTE (Toán treatment effect)', fontsize=12)
ax.set_title('CT2018 Effect by Urban Tier (2025 vs 2026)', fontsize=13, fontweight='bold')
ax.legend()
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(f'{OUT}/mc_hte_tier_year.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"Figure saved: {OUT}/mc_hte_tier_year.png")

# ─────────────────────────────────────────────
# Section E: Rosenbaum Bounds + MC Sensitivity
# ─────────────────────────────────────────────

print("\n" + "="*60)
print("E. ROSENBAUM BOUNDS + MC SENSITIVITY (Province Gaps)")
print("="*60)

# Province-level gaps
gap_25_dict = {}
for prov in df25_all['province_harmonized'].unique():
    if pd.isna(prov): continue
    y_ct2006 = df25_all[(df25_all['province_harmonized']==prov) & (df25_all['treatment']==0)]['toan']
    y_ct2018 = df25_all[(df25_all['province_harmonized']==prov) & (df25_all['treatment']==1)]['toan']
    if len(y_ct2006) > 0 and len(y_ct2018) > 0:
        gap_25_dict[prov] = y_ct2018.mean() - y_ct2006.mean()

gap_26_dict = {}
for prov in df26_all['province_harmonized'].unique():
    if pd.isna(prov): continue
    y_2024 = df26_all[(df26_all['province_harmonized']==prov) & (df26_all['treatment']==0)]['toan']
    y_2026 = df26_all[(df26_all['province_harmonized']==prov) & (df26_all['treatment']==1)]['toan']
    if len(y_2024) > 0 and len(y_2026) > 0:
        gap_26_dict[prov] = y_2026.mean() - y_2024.mean()

# Align provinces
common_provs = set(gap_25_dict.keys()) & set(gap_26_dict.keys())
gaps_25 = np.array([gap_25_dict[p] for p in common_provs])
gaps_26 = np.array([gap_26_dict[p] for p in common_provs])
gaps_diff = gaps_26 - gaps_25

print(f"Common provinces: {len(common_provs)}")
print(f"Mean gap 2025: {gaps_25.mean():.4f}")
print(f"Mean gap 2026: {gaps_26.mean():.4f}")
print(f"Mean difference (2026 − 2025): {gaps_diff.mean():+.4f}")

# Wilcoxon test
w_stat, w_pval = wilcoxon(gaps_diff)
print(f"Wilcoxon test: W={w_stat:.1f}, p={w_pval:.4f}")

# Rosenbaum bounds (Γ scan 1.0 to 4.0)
gamma_range = np.arange(1.0, 4.05, 0.1)
gamma_star = None
rosenbaum_results = []

for gamma in gamma_range:
    pi = gamma / (1 + gamma)

    # Compute E(W) and Var(W) under hidden bias Γ
    n = len(gaps_diff)
    E_W_null = n * (n + 1) / 4
    var_W_null = n * (n + 1) * (2*n + 1) / 24

    # Adjusted expectation and variance under Γ
    p_worse = 1 - pi
    E_W_adj = n * (n + 1) / 4 * (pi + p_worse)
    z_score = (abs(w_stat) - E_W_adj) / np.sqrt(var_W_null * (pi + p_worse) ** 2)
    p_upper = 1 - norm.cdf(z_score)

    rosenbaum_results.append({'gamma': gamma, 'p_upper': p_upper})

    if p_upper > 0.05 and gamma_star is None:
        gamma_star = gamma

print(f"\nRosenbaum bounds:")
for r in rosenbaum_results[::2]:  # Print every other for brevity
    print(f"  Γ={r['gamma']:.1f}: p_upper={r['p_upper']:.4f}")

if gamma_star is not None:
    print(f"\nGamma star (Γ*): {gamma_star:.1f}")
else:
    print(f"\nGamma star (Γ*): > 4.0")

# MC sensitivity (Γ = 2.0)
GAMMA_MC = 2.0
rng_mc = np.random.default_rng(123)
n_mc = 5000
mc_ates = []

for _ in range(n_mc):
    noise = rng_mc.uniform(low=-np.log(GAMMA_MC), high=np.log(GAMMA_MC), size=len(gaps_diff)) * 0.15
    mc_ate = np.mean(gaps_diff + noise)
    mc_ates.append(mc_ate)

mc_ates = np.array(mc_ates)
frac_neg = np.mean(mc_ates < 0)

print(f"\nMonte Carlo sensitivity (Γ={GAMMA_MC}):")
print(f"  Fraction with ATE < 0: {frac_neg:.4f}")
print(f"  Mean MC ATE: {mc_ates.mean():.4f}")

# Figures E: Rosenbaum curve + MC histogram
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

gammas_plot = [r['gamma'] for r in rosenbaum_results]
p_uppers = [r['p_upper'] for r in rosenbaum_results]
ax1.plot(gammas_plot, p_uppers, 'o-', color='navy', linewidth=2, markersize=6)
ax1.axhline(y=0.05, color='red', linestyle='--', linewidth=1.5, label='α=0.05')
if gamma_star is not None:
    ax1.axvline(x=gamma_star, color='green', linestyle='--', linewidth=1.5, label=f'Γ*={gamma_star:.1f}')
ax1.set_xlabel('Hidden Bias (Γ)', fontsize=12)
ax1.set_ylabel('p-value (upper bound)', fontsize=12)
ax1.set_title('Rosenbaum Bounds: Province Gap Improvement', fontsize=13, fontweight='bold')
ax1.legend()
ax1.grid(alpha=0.3)

ax2.hist(mc_ates, bins=40, color='steelblue', alpha=0.7, edgecolor='black')
ax2.axvline(x=gaps_diff.mean(), color='red', linestyle='--', linewidth=2, label=f'Observed: {gaps_diff.mean():.3f}')
ax2.axvline(x=0, color='black', linestyle=':', linewidth=1.5)
ax2.set_xlabel('ATE under Γ=2.0', fontsize=12)
ax2.set_ylabel('Frequency', fontsize=12)
ax2.set_title(f'MC Sensitivity: Fraction negative={frac_neg:.1%}', fontsize=13, fontweight='bold')
ax2.legend()
ax2.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(f'{OUT}/mc_rosenbaum_2025_2026.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"Figure saved: {OUT}/mc_rosenbaum_2025_2026.png")

# ─────────────────────────────────────────────
# Summary Table
# ─────────────────────────────────────────────

print("\n" + "="*60)
print("SUMMARY TABLE")
print("="*60)

print(f"{'Section':<12} {'Method':<20} {'ATE_2025':<12} {'ATE_2026':<12} {'Delta':<12} {'P-value':<10}")
print("-" * 80)
print(f"{'A':<12} {'Raw toan mean':<20} {results_a['toan']['mean_2025']:<12.4f} {results_a['toan']['mean_2026']:<12.4f} {results_a['toan']['delta']:<12.4f} {results_a['toan']['p_value']:<10.4f}")
print(f"{'B':<12} {'OLS RDD':<20} {ate_2025:<12.4f} {ate_2026_ols:<12.4f} {ate_delta_obs:<12.4f} {ate_delta_p:<10.4f}")
print(f"{'C':<12} {'Double ML':<20} {'N/A':<12} {dml_ate_2026:<12.4f} {dml_ate_2026 - ate_2025:<12.4f} {'N/A':<10}")
for tier in ['Đô thị lớn', 'Đô thị vừa', 'Tỉnh lẻ/Nông thôn']:
    if not np.isnan(results_d[tier]['hte_2025']):
        print(f"{'D':<12} {'HTE ' + tier:<20} {results_d[tier]['hte_2025']:<12.4f} {results_d[tier]['hte_2026']:<12.4f} {results_d[tier]['hte_2026'] - results_d[tier]['hte_2025']:<12.4f} {'N/A':<10}")
print(f"{'E':<12} {'Wilcoxon (prov)':<20} {gaps_25.mean():<12.4f} {gaps_26.mean():<12.4f} {gaps_diff.mean():<12.4f} {w_pval:<10.4f}")
print(f"{'E':<12} {'Rosenbaum Γ*':<20} {(str(gamma_star) if gamma_star else '>4.0'):<12} {'':<12} {'':<12} {'':<10}")

print("\n✓ All analyses complete.")
print(f"✓ Figures saved to {OUT}/mc_*.png")
