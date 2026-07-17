"""
Causal ML Analysis: Vietnam University Entrance Exam Scores
===========================================================
Analyses:
  1. RDD  — CT2018 curriculum effect (2025 natural experiment + 2024 vs 2025)
  2. Double ML — Urban/Rural causal effect on math score (2021-2024)
  3. HTE  — CT2018 effect by urban tier
  4. Bootstrap DiD CIs — Urban vs Rural COVID recovery

econml is NOT required; manual double-ML is implemented as fallback (and default).
"""

import os
import sys
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
import statsmodels.api as sm
from scipy import stats
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import KFold
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings('ignore')

sys.path.insert(0, '/home/tienda/WorkSpace/HCMUS/PTDLTM')
from province_mapping import (
    PROVINCE_NAMES_OLD as PROVINCE_NAMES,
    CHUYEN_STRONG_OLD as CHUYEN_STRONG,
    FEE_EXEMPT_OLD as FEE_EXEMPT,
    OLD_TO_NEW_2026,
    urban_tier_old, urban_tier_2026,
)

OUT  = '/home/tienda/WorkSpace/HCMUS/PTDLTM/figures'
BASE = '/home/tienda/WorkSpace/HCMUS/PTDLTM/GraduationExamScoreProcessing/Results'
os.makedirs(OUT, exist_ok=True)

# ── Try to import econml; fall back gracefully ─────────────────────────────────
ECONML_AVAILABLE = False
try:
    from econml.dml import LinearDML
    ECONML_AVAILABLE = True
    print("econml available — will use LinearDML for Double ML")
except ImportError:
    print("econml not available — using manual Double ML (2-stage residual regression)")

# ──────────────────────────────────────────────────────────────────────────────
# DATA LOADING  (same pattern as analysis.py)
# ──────────────────────────────────────────────────────────────────────────────

def _rename_common(df: pd.DataFrame) -> pd.DataFrame:
    rename = {
        'ngu_van': 'nguvan', 'ngoai_ngu': 'ngoaingu',
        'vat_ly':  'vatly',  'hoa_hoc':  'hoahoc',
        'sinh_hoc':'sinhhoc','lich_su':  'lichsu',  'dia_ly': 'dialy',
        'vat_li':  'vatly',  'dia_li':   'dialy',
    }
    df.columns = df.columns.str.lower().str.strip()
    return df.rename(columns={k: v for k, v in rename.items() if k in df.columns})


def load_2021() -> pd.DataFrame:
    df = pd.read_csv(f'{BASE}/Diemthi2021.csv', dtype={'SBD': str, 'Cum_thi': str})
    df = _rename_common(df)
    df['province'] = df['cum_thi'].str.zfill(2).str[:2].apply(
        lambda x: int(x) if x.isdigit() else np.nan)
    df['year'] = 2021
    return df


def load_2022() -> pd.DataFrame:
    df = pd.read_csv(f'{BASE}/Diemthi2022.csv', dtype={'sbd': str})
    df = _rename_common(df)
    df['province'] = df['sbd'].str[:2].apply(lambda x: int(x) if x.isdigit() else np.nan)
    df['year'] = 2022
    return df


def load_2024() -> pd.DataFrame:
    df = pd.read_csv(f'{BASE}/2024/Diemthi2024.csv', dtype={'sbd': str})
    df = _rename_common(df)
    df['province'] = df['sbd'].str[:2].apply(lambda x: int(x) if x.isdigit() else np.nan)
    df['year'] = 2024
    return df


def load_2025_ct2006() -> pd.DataFrame:
    df = pd.read_csv(
        f'{BASE}/2025/20250715-ketquathi-ct2006.csv',
        sep=';', dtype={'sbd': str}, encoding='utf-8-sig')
    df = _rename_common(df)
    df['province'] = df['sbd'].str[:2].apply(lambda x: int(x) if x.isdigit() else np.nan)
    df['year'] = 2025
    df['curriculum'] = 'CT2006'
    df['treatment'] = 0
    return df


def load_2025_ct2018() -> pd.DataFrame:
    df = pd.read_csv(
        f'{BASE}/2025/20250715-ketquathi-ct2018a.csv',
        sep=';', dtype={'sbd': str}, encoding='utf-8-sig')
    df = _rename_common(df)
    df['province'] = df['sbd'].str[:2].apply(lambda x: int(x) if x.isdigit() else np.nan)
    df['year'] = 2025
    df['curriculum'] = 'CT2018'
    df['treatment'] = 1
    return df


SUBJECTS = ['toan', 'nguvan', 'ngoaingu', 'vatly', 'hoahoc', 'sinhhoc', 'lichsu', 'dialy', 'gdcd']


def _enrich(df: pd.DataFrame, use_2026_codes: bool = False) -> pd.DataFrame:
    """Add urban_tier, is_chuyen_province, province_harmonized columns."""
    for col in SUBJECTS:
        if col not in df.columns:
            df[col] = np.nan
        else:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    if use_2026_codes:
        from province_mapping import urban_tier_2026, CHUYEN_STRONG_2026
        df['urban_tier'] = df['province'].apply(
            lambda p: urban_tier_2026(int(p)) if pd.notna(p) else 'Unknown')
        df['is_chuyen_province'] = df['province'].apply(
            lambda p: int(p) in CHUYEN_STRONG_2026 if pd.notna(p) else False)
        df['province_harmonized'] = df['province'].astype('Int64')
    else:
        df['urban_tier'] = df['province'].apply(
            lambda p: urban_tier_old(int(p)) if pd.notna(p) else 'Unknown')
        df['is_chuyen_province'] = df['province'].apply(
            lambda p: int(p) in CHUYEN_STRONG if pd.notna(p) else False)
        df['province_harmonized'] = df['province'].map(OLD_TO_NEW_2026)
    return df


print("\nLoading data...")
df21  = _enrich(load_2021())
df22  = _enrich(load_2022())
df24  = _enrich(load_2024())
df25_ct2006  = _enrich(load_2025_ct2006())
df25_ct2018  = _enrich(load_2025_ct2018())
df25_all     = pd.concat([df25_ct2006, df25_ct2018], ignore_index=True)

for label, df in [('2021', df21), ('2022', df22), ('2024', df24),
                  ('2025-CT2006', df25_ct2006), ('2025-CT2018', df25_ct2018)]:
    print(f"  {label}: {len(df):,} rows")


# ══════════════════════════════════════════════════════════════════════════════
# ANALYSIS 1: REGRESSION DISCONTINUITY DESIGN
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("ANALYSIS 1: REGRESSION DISCONTINUITY — CT2018 CURRICULUM EFFECT")
print("="*70)

# ── 1A: Within-2025 RDD (sharp discontinuity: curriculum assignment) ──────────
print("\n--- 1A: Within-2025 sharp RDD (CT2018 vs CT2006) ---")

rdd_25 = df25_all.dropna(subset=['toan', 'province']).copy()
rdd_25['urban_large'] = (rdd_25['urban_tier'] == 'Đô thị lớn').astype(int)
rdd_25['urban_mid']   = (rdd_25['urban_tier'] == 'Đô thị vừa').astype(int)
rdd_25['is_chuyen']   = rdd_25['is_chuyen_province'].astype(int)

model_rdd_25 = smf.ols(
    'toan ~ treatment + urban_large + urban_mid + is_chuyen',
    data=rdd_25
).fit(cov_type='HC3')

treat_coef  = model_rdd_25.params['treatment']
treat_se    = model_rdd_25.bse['treatment']
treat_p     = model_rdd_25.pvalues['treatment']
treat_ci_lo = model_rdd_25.conf_int().loc['treatment', 0]
treat_ci_hi = model_rdd_25.conf_int().loc['treatment', 1]

ct06_mean = rdd_25[rdd_25['treatment']==0]['toan'].mean()
ct18_mean = rdd_25[rdd_25['treatment']==1]['toan'].mean()
raw_diff  = ct18_mean - ct06_mean

print(f"  CT2006 mean toan: {ct06_mean:.4f}  n={len(rdd_25[rdd_25['treatment']==0]):,}")
print(f"  CT2018 mean toan: {ct18_mean:.4f}  n={len(rdd_25[rdd_25['treatment']==1]):,}")
print(f"  Raw difference (CT2018 - CT2006): {raw_diff:+.4f}")
print(f"\n  RDD OLS (HC3 robust SEs):")
print(f"    ATE (treatment coef): {treat_coef:+.4f}")
print(f"    Std. Error:           {treat_se:.4f}")
print(f"    p-value:              {treat_p:.4e}")
print(f"    95% CI:               [{treat_ci_lo:+.4f}, {treat_ci_hi:+.4f}]")
print(f"    R²:                   {model_rdd_25.rsquared:.4f}")

mw_stat, mw_p = stats.mannwhitneyu(
    rdd_25[rdd_25['treatment']==1]['toan'].dropna(),
    rdd_25[rdd_25['treatment']==0]['toan'].dropna(),
    alternative='two-sided')
print(f"\n  Mann-Whitney U (CT2018 vs CT2006 toan): p={mw_p:.4e}")

# Province-level means for RDD scatter plot
prov_rdd = rdd_25.groupby(['province', 'treatment']).agg(
    toan_mean=('toan', 'mean'),
    n=('toan', 'count')
).reset_index().query('n >= 50')

# ── 1B: 2024 vs 2025-CT2018 year-level RDD ───────────────────────────────────
print("\n--- 1B: Year-level RDD (2024 CT2006 baseline vs 2025 CT2018) ---")

df24_rdd = df24.dropna(subset=['toan', 'province']).copy()
df24_rdd['treatment'] = 0
df25_ct2018_rdd = df25_ct2018.dropna(subset=['toan', 'province']).copy()
df25_ct2018_rdd['treatment'] = 1

rdd_yr = pd.concat([df24_rdd, df25_ct2018_rdd], ignore_index=True)
rdd_yr['urban_large'] = (rdd_yr['urban_tier'] == 'Đô thị lớn').astype(int)
rdd_yr['urban_mid']   = (rdd_yr['urban_tier'] == 'Đô thị vừa').astype(int)
rdd_yr['is_chuyen']   = rdd_yr['is_chuyen_province'].astype(int)

model_rdd_yr = smf.ols(
    'toan ~ treatment + urban_large + urban_mid + is_chuyen',
    data=rdd_yr
).fit(cov_type='HC3')

yr_coef  = model_rdd_yr.params['treatment']
yr_se    = model_rdd_yr.bse['treatment']
yr_p     = model_rdd_yr.pvalues['treatment']
yr_ci_lo = model_rdd_yr.conf_int().loc['treatment', 0]
yr_ci_hi = model_rdd_yr.conf_int().loc['treatment', 1]

print(f"  2024 (CT2006) mean toan: {df24_rdd['toan'].mean():.4f}  n={len(df24_rdd):,}")
print(f"  2025 (CT2018) mean toan: {df25_ct2018_rdd['toan'].mean():.4f}  n={len(df25_ct2018_rdd):,}")
print(f"\n  Year-level RDD OLS (HC3 robust SEs):")
print(f"    Coef (2025 CT2018 vs 2024): {yr_coef:+.4f}")
print(f"    Std. Error:                 {yr_se:.4f}")
print(f"    p-value:                    {yr_p:.4e}")
print(f"    95% CI:                     [{yr_ci_lo:+.4f}, {yr_ci_hi:+.4f}]")

prov_yr_means = rdd_yr.groupby(['province', 'treatment'])['toan'].mean().reset_index()


# ══════════════════════════════════════════════════════════════════════════════
# ANALYSIS 2: DOUBLE ML — URBAN CAUSAL EFFECT ON MATH SCORE
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("ANALYSIS 2: DOUBLE ML — CAUSAL EFFECT OF URBAN LOCATION ON MATH")
print("="*70)

dml_df = pd.concat([df21, df22, df24], ignore_index=True).dropna(subset=['toan', 'province']).copy()
dml_df['urban_large'] = (dml_df['urban_tier'] == 'Đô thị lớn').astype(int)
dml_df['year_norm']   = (dml_df['year'] - 2022) / 1.0
dml_df['is_chuyen']   = dml_df['is_chuyen_province'].astype(int)
dml_df['urban_mid']   = (dml_df['urban_tier'] == 'Đô thị vừa').astype(int)

print(f"\n  Dataset: 2021+2022+2024, n={len(dml_df):,}")
print(f"  Treatment: urban_large (1 = Đô thị lớn)")
print(f"  Urban large: {dml_df['urban_large'].sum():,} students "
      f"({dml_df['urban_large'].mean()*100:.1f}%)")

# ── Naive OLS benchmark ───────────────────────────────────────────────────────
ols_naive = smf.ols(
    'toan ~ urban_large + urban_mid + is_chuyen + year_norm',
    data=dml_df
).fit(cov_type='HC3')
ols_ate       = ols_naive.params['urban_large']
ols_ate_se    = ols_naive.bse['urban_large']
ols_ate_ci_lo = ols_naive.conf_int().loc['urban_large', 0]
ols_ate_ci_hi = ols_naive.conf_int().loc['urban_large', 1]
ols_ate_p     = ols_naive.pvalues['urban_large']

print(f"\n  Naive OLS estimate:")
print(f"    urban_large coef: {ols_ate:+.4f}  SE={ols_ate_se:.4f}  p={ols_ate_p:.4e}")
print(f"    95% CI: [{ols_ate_ci_lo:+.4f}, {ols_ate_ci_hi:+.4f}]")

# ── Double ML (manual 2-stage residual regression with cross-fitting) ─────────
print(f"\n  Double ML (manual cross-fitting, n_splits=5, GBM first stage):")

X_cols = ['year_norm', 'is_chuyen', 'urban_mid']
Y_col  = 'toan'
T_col  = 'urban_large'

X_full = dml_df[X_cols].values
Y_full = dml_df[Y_col].values
T_full = dml_df[T_col].values

# Sample for speed on large datasets
N = len(dml_df)
if N > 300_000:
    rng_s = np.random.RandomState(42)
    idx   = rng_s.choice(N, 300_000, replace=False)
    X, Y, T = X_full[idx], Y_full[idx], T_full[idx]
    print(f"    (Sampled 300,000 of {N:,} rows for speed)")
else:
    X, Y, T = X_full, Y_full, T_full

scaler = StandardScaler()
X_sc   = scaler.fit_transform(X)

kf    = KFold(n_splits=5, shuffle=True, random_state=42)
Y_res = np.zeros(len(Y), dtype=float)
T_res = np.zeros(len(T), dtype=float)

for fold, (train_idx, test_idx) in enumerate(kf.split(X_sc)):
    m_y = GradientBoostingRegressor(n_estimators=100, max_depth=3, random_state=42)
    m_y.fit(X_sc[train_idx], Y[train_idx])
    Y_res[test_idx] = Y[test_idx] - m_y.predict(X_sc[test_idx])

    m_t = GradientBoostingRegressor(n_estimators=100, max_depth=3, random_state=42)
    m_t.fit(X_sc[train_idx], T[train_idx])
    T_res[test_idx] = T[test_idx] - m_t.predict(X_sc[test_idx])

    print(f"    Fold {fold+1}/5 done  "
          f"(Y_res std={Y_res[test_idx].std():.3f}, T_res std={T_res[test_idx].std():.3f})")

# Second stage: regress Y_residual on T_residual
T_res_2d = T_res.reshape(-1, 1)
stage2   = LinearRegression().fit(T_res_2d, Y_res)
dml_ate  = stage2.coef_[0]

n_obs     = len(Y_res)
resid2    = Y_res - stage2.predict(T_res_2d)
sigma2    = np.sum(resid2**2) / (n_obs - 2)
var_T_res = np.sum(T_res**2)
dml_ate_se = np.sqrt(sigma2 / var_T_res)
dml_z      = dml_ate / dml_ate_se
dml_p      = 2 * (1 - stats.norm.cdf(abs(dml_z)))
dml_ci_lo  = dml_ate - 1.96 * dml_ate_se
dml_ci_hi  = dml_ate + 1.96 * dml_ate_se

print(f"\n  Double ML ATE (urban_large effect on toan):")
print(f"    ATE:    {dml_ate:+.4f}")
print(f"    SE:     {dml_ate_se:.4f}")
print(f"    z:      {dml_z:+.3f}")
print(f"    p:      {dml_p:.4e}")
print(f"    95% CI: [{dml_ci_lo:+.4f}, {dml_ci_hi:+.4f}]")
print(f"\n  Debiasing effect (OLS - DML): {ols_ate - dml_ate:+.4f} points")
print(f"    (positive = OLS overstates urban benefit due to confounders)")


# ══════════════════════════════════════════════════════════════════════════════
# ANALYSIS 3: HTE — CT2018 EFFECT BY URBAN TIER
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("ANALYSIS 3: HETEROGENEOUS TREATMENT EFFECTS — CT2018 BY URBAN TIER")
print("="*70)

hte_data = df25_all.dropna(subset=['toan', 'province']).copy()
hte_data['is_chuyen'] = hte_data['is_chuyen_province'].astype(int)

tiers       = ['Đô thị lớn', 'Đô thị vừa', 'Tỉnh lẻ/Nông thôn']
hte_results = []

print("\n  Treatment effect per urban tier (OLS, HC3 robust SEs):")
for tier in tiers:
    sub = hte_data[hte_data['urban_tier'] == tier]
    if len(sub) < 200:
        print(f"  {tier}: insufficient data (n={len(sub)})")
        continue
    m     = smf.ols('toan ~ treatment + is_chuyen', data=sub).fit(cov_type='HC3')
    coef  = m.params['treatment']
    se    = m.bse['treatment']
    p     = m.pvalues['treatment']
    ci_lo = m.conf_int().loc['treatment', 0]
    ci_hi = m.conf_int().loc['treatment', 1]
    ct06_m = sub[sub['treatment']==0]['toan'].mean()
    ct18_m = sub[sub['treatment']==1]['toan'].mean()
    n0 = (sub['treatment']==0).sum()
    n1 = (sub['treatment']==1).sum()
    hte_results.append({
        'tier': tier, 'coef': coef, 'se': se, 'p': p,
        'ci_lo': ci_lo, 'ci_hi': ci_hi,
        'ct06_mean': ct06_m, 'ct18_mean': ct18_m, 'n0': n0, 'n1': n1
    })
    sig = "***" if p < 0.001 else ("**" if p < 0.01 else ("*" if p < 0.05 else "ns"))
    print(f"\n  [{tier}]  n_CT2006={n0:,}  n_CT2018={n1:,}")
    print(f"    CT2006 mean: {ct06_m:.4f}  CT2018 mean: {ct18_m:.4f}")
    print(f"    ATE: {coef:+.4f}  SE={se:.4f}  p={p:.4e}  {sig}")
    print(f"    95% CI: [{ci_lo:+.4f}, {ci_hi:+.4f}]")

# Interaction test
print("\n  Interaction test: treatment × urban_large")
hte_int = hte_data.copy()
hte_int['urban_large'] = (hte_int['urban_tier'] == 'Đô thị lớn').astype(int)
hte_int['urban_mid']   = (hte_int['urban_tier'] == 'Đô thị vừa').astype(int)
hte_int['tx_urban']    = hte_int['treatment'] * hte_int['urban_large']
hte_int['tx_mid']      = hte_int['treatment'] * hte_int['urban_mid']

m_int = smf.ols(
    'toan ~ treatment + urban_large + urban_mid + tx_urban + tx_mid + is_chuyen',
    data=hte_int
).fit(cov_type='HC3')

for term in ['treatment', 'urban_large', 'urban_mid', 'tx_urban', 'tx_mid']:
    if term in m_int.params:
        c = m_int.params[term]
        p = m_int.pvalues[term]
        sig = "***" if p < 0.001 else ("**" if p < 0.01 else ("*" if p < 0.05 else "ns"))
        print(f"    {term:15s}: {c:+.4f}  p={p:.4e}  {sig}")


# ══════════════════════════════════════════════════════════════════════════════
# ANALYSIS 4: BOOTSTRAP DiD — URBAN vs RURAL COVID RECOVERY
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("ANALYSIS 4: BOOTSTRAP DiD — URBAN vs RURAL COVID RECOVERY (2021→2024)")
print("="*70)

did_df = pd.concat([df21, df24], ignore_index=True)[
    ['year', 'urban_tier', 'toan', 'province_harmonized']
].dropna().copy()
did_df = did_df[did_df['urban_tier'].isin(['Đô thị lớn', 'Tỉnh lẻ/Nông thôn'])]

piv = did_df.groupby(['year', 'urban_tier'])['toan'].mean().unstack()
if 'Đô thị lớn' in piv.columns and 'Tỉnh lẻ/Nông thôn' in piv.columns:
    did_point   = (
        (piv.loc[2024, 'Đô thị lớn']        - piv.loc[2021, 'Đô thị lớn']) -
        (piv.loc[2024, 'Tỉnh lẻ/Nông thôn'] - piv.loc[2021, 'Tỉnh lẻ/Nông thôn'])
    )
    urban_delta = piv.loc[2024, 'Đô thị lớn']        - piv.loc[2021, 'Đô thị lớn']
    rural_delta = piv.loc[2024, 'Tỉnh lẻ/Nông thôn'] - piv.loc[2021, 'Tỉnh lẻ/Nông thôn']
    print(f"\n  Point estimate DiD: {did_point:+.4f}")
    print(f"    Urban recovery (2021→2024):  {urban_delta:+.4f}")
    print(f"    Rural recovery (2021→2024):  {rural_delta:+.4f}")
else:
    did_point = np.nan
    print("  Could not compute DiD: missing urban tier data")

print(f"\n  Running cluster bootstrap (1,000 iterations, clustered by province)...")
provinces = did_df['province_harmonized'].dropna().unique()
rng_boot  = np.random.RandomState(123)
boot_dids = []

for i in range(1000):
    sampled_provs = rng_boot.choice(provinces, size=len(provinces), replace=True)
    frames        = [did_df[did_df['province_harmonized'] == p] for p in sampled_provs]
    boot_sample   = pd.concat(frames, ignore_index=True)
    piv_b = boot_sample.groupby(['year', 'urban_tier'])['toan'].mean().unstack()
    try:
        did_b = (
            (piv_b.loc[2024, 'Đô thị lớn']        - piv_b.loc[2021, 'Đô thị lớn']) -
            (piv_b.loc[2024, 'Tỉnh lẻ/Nông thôn'] - piv_b.loc[2021, 'Tỉnh lẻ/Nông thôn'])
        )
        boot_dids.append(did_b)
    except (KeyError, TypeError):
        pass

boot_arr   = np.array(boot_dids)
boot_mean  = np.mean(boot_arr)
boot_std   = np.std(boot_arr)
boot_ci_lo = np.percentile(boot_arr, 2.5)
boot_ci_hi = np.percentile(boot_arr, 97.5)

print(f"\n  Bootstrap results (n_valid_iters={len(boot_dids)}):")
print(f"    Original point estimate: {did_point:+.4f}")
print(f"    Bootstrap mean:          {boot_mean:+.4f}")
print(f"    Bootstrap std:           {boot_std:.4f}")
print(f"    95% CI (percentile):     [{boot_ci_lo:+.4f}, {boot_ci_hi:+.4f}]")
sig_did = boot_ci_lo > 0 or boot_ci_hi < 0
print(f"    Significant (CI excludes 0): {'YES' if sig_did else 'NO'}")


# ══════════════════════════════════════════════════════════════════════════════
# FIGURES
# ══════════════════════════════════════════════════════════════════════════════
print("\nGenerating figures...")
COLORS = {
    'CT2006': '#457b9d',
    'CT2018': '#e63946',
    'ols':    '#2a9d8f',
    'dml':    '#e9c46a',
    'urban':  '#e63946',
    'mid':    '#457b9d',
    'rural':  '#2a9d8f',
}
plt.rcParams.update({'font.size': 11})

# ── FIG 1: rdd_curriculum_effect.png ─────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(15, 6))
fig.suptitle('RDD — Curriculum Effect (CT2018 vs CT2006)', fontweight='bold', fontsize=13)

ax = axes[0]
ax.set_title('Panel A: Within-2025 Province Means', fontsize=11)
for treat_val, label, color in [(0, 'CT2006', COLORS['CT2006']), (1, 'CT2018', COLORS['CT2018'])]:
    sub = prov_rdd[prov_rdd['treatment'] == treat_val]
    ax.scatter(sub['province'], sub['toan_mean'],
               label=f'{label} (mu={sub["toan_mean"].mean():.3f})',
               alpha=0.7, s=60, color=color)
ax.axhline(ct06_mean, color=COLORS['CT2006'], linestyle='--', alpha=0.5, linewidth=1.5)
ax.axhline(ct18_mean, color=COLORS['CT2018'], linestyle='--', alpha=0.5, linewidth=1.5)
ax.set_xlabel('Province code (exam)')
ax.set_ylabel('Mean Toan score')
ax.legend(fontsize=9)
ax.grid(alpha=0.3)
xlim = ax.get_xlim()
ax.annotate('', xy=(xlim[1]*0.97, ct18_mean), xytext=(xlim[1]*0.97, ct06_mean),
            arrowprops=dict(arrowstyle='<->', color='black', lw=1.5))
ax.text(xlim[1]*0.97, (ct06_mean+ct18_mean)/2,
        f'  ATE={treat_coef:+.3f}\n  p={treat_p:.2e}', va='center', fontsize=9)

ax = axes[1]
ax.set_title('Panel B: 2024 (CT2006) vs 2025 (CT2018) Province Means', fontsize=11)
for treat_val, label, color in [
    (0, '2024 CT2006', COLORS['CT2006']),
    (1, '2025 CT2018', COLORS['CT2018'])
]:
    sub = prov_yr_means[prov_yr_means['treatment'] == treat_val]
    ax.scatter(sub['province'], sub['toan'],
               label=f'{label} (mu={sub["toan"].mean():.3f})',
               alpha=0.7, s=50, color=color)
m24 = df24_rdd['toan'].mean()
m25 = df25_ct2018_rdd['toan'].mean()
ax.axhline(m24, color=COLORS['CT2006'], linestyle='--', alpha=0.5, linewidth=1.5)
ax.axhline(m25, color=COLORS['CT2018'], linestyle='--', alpha=0.5, linewidth=1.5)
ax.set_xlabel('Province code (exam)')
ax.set_ylabel('Mean Toan score')
ax.legend(fontsize=9)
ax.grid(alpha=0.3)
xlim2 = ax.get_xlim()
ax.annotate('', xy=(xlim2[1]*0.97, m25), xytext=(xlim2[1]*0.97, m24),
            arrowprops=dict(arrowstyle='<->', color='black', lw=1.5))
ax.text(xlim2[1]*0.97, (m24+m25)/2,
        f'  ATE={yr_coef:+.3f}\n  p={yr_p:.2e}', va='center', fontsize=9)

fig.tight_layout()
fig.savefig(f'{OUT}/rdd_curriculum_effect.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"  Saved rdd_curriculum_effect.png")

# ── FIG 2: dml_urban_effect.png ───────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(13, 6))
fig.suptitle('Double ML — Causal Effect of Urban Location on Math Score',
             fontweight='bold', fontsize=13)

ax = axes[0]
ax.set_title('ATE: Naive OLS vs Double ML', fontsize=11)
bar_labels = ['Naive OLS', 'Double ML\n(GBM, 5-fold)']
ates   = [ols_ate,     dml_ate]
ci_los = [ols_ate_ci_lo, dml_ci_lo]
ci_his = [ols_ate_ci_hi, dml_ci_hi]
colors_bar = [COLORS['ols'], COLORS['dml']]

ax.bar(range(2), ates, color=colors_bar, alpha=0.85, width=0.5)
err_lo = [abs(a - b) for a, b in zip(ates, ci_los)]
err_hi = [abs(b - a) for a, b in zip(ates, ci_his)]
ax.errorbar(range(2), ates,
            yerr=[err_lo, err_hi],
            fmt='none', color='black', capsize=8, linewidth=2)
ax.axhline(0, color='gray', linestyle='--', linewidth=1)
ax.set_xticks([0, 1])
ax.set_xticklabels(bar_labels)
ax.set_ylabel('ATE: Urban effect on Toan score')
for i, (ate, se) in enumerate(zip(ates, [ols_ate_se, dml_ate_se])):
    ax.text(i, ate + (0.05 if ate >= 0 else -0.1),
            f'{ate:+.3f}\n(SE={se:.3f})', ha='center', fontsize=10, fontweight='bold')
ax.grid(axis='y', alpha=0.3)

ax2 = axes[1]
ax2.set_title('2nd Stage: Y-residual vs T-residual\n(slope = DML ATE)', fontsize=11)
plot_n = min(5000, len(T_res))
ax2.scatter(T_res[:plot_n], Y_res[:plot_n], alpha=0.08, s=5, color=COLORS['dml'])
x_line = np.linspace(T_res.min(), T_res.max(), 100)
ax2.plot(x_line, dml_ate * x_line, color='black', linewidth=2,
         label=f'Slope = ATE = {dml_ate:+.3f}')
ax2.set_xlabel('T Residual (Urban - E[Urban|X])')
ax2.set_ylabel('Y Residual (Toan - E[Toan|X])')
ax2.legend()
ax2.grid(alpha=0.3)

fig.tight_layout()
fig.savefig(f'{OUT}/dml_urban_effect.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"  Saved dml_urban_effect.png")

# ── FIG 3: hte_curriculum_by_tier.png ────────────────────────────────────────
if hte_results:
    fig, axes = plt.subplots(1, 2, figsize=(13, 6))
    fig.suptitle('HTE — CT2018 Curriculum Effect by Urban Tier',
                 fontweight='bold', fontsize=13)

    tier_colors_hte = [COLORS['urban'], COLORS['mid'], COLORS['rural']]
    r_labels = [
        r['tier'].replace('Tỉnh lẻ/Nông thôn', 'Tinh le/NT')
                 .replace('Đô thị lớn', 'Do thi lon')
                 .replace('Đô thị vừa', 'Do thi vua')
        for r in hte_results
    ]

    ax = axes[0]
    ax.set_title('ATE (CT2018 - CT2006) with 95% CI', fontsize=11)
    x_pos = list(range(len(hte_results)))
    r_coefs  = [r['coef']  for r in hte_results]
    r_ci_lo  = [r['ci_lo'] for r in hte_results]
    r_ci_hi  = [r['ci_hi'] for r in hte_results]
    ax.bar(x_pos, r_coefs, color=tier_colors_hte[:len(hte_results)], alpha=0.85, width=0.5)
    hte_err_lo = [abs(c - lo) for c, lo in zip(r_coefs, r_ci_lo)]
    hte_err_hi = [abs(hi - c) for c, hi in zip(r_coefs, r_ci_hi)]
    ax.errorbar(x_pos, r_coefs,
                yerr=[hte_err_lo, hte_err_hi],
                fmt='none', color='black', capsize=8, linewidth=2)
    ax.axhline(0, color='gray', linestyle='--')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(r_labels, fontsize=9)
    ax.set_ylabel('ATE on Toan score')
    for i, r in enumerate(hte_results):
        sig = "***" if r['p'] < 0.001 else ("**" if r['p'] < 0.01 else ("*" if r['p'] < 0.05 else "ns"))
        y_off = 0.03 if r['coef'] >= 0 else -0.06
        ax.text(i, r['coef'] + y_off, f"{r['coef']:+.3f}\n{sig}",
                ha='center', fontsize=10, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)

    ax2 = axes[1]
    ax2.set_title('Mean Toan by Curriculum & Tier', fontsize=11)
    n_tiers  = len(hte_results)
    x        = np.arange(n_tiers)
    width    = 0.35
    ct06_ms  = [r['ct06_mean'] for r in hte_results]
    ct18_ms  = [r['ct18_mean'] for r in hte_results]
    ax2.bar(x - width/2, ct06_ms, width, label='CT2006', color=COLORS['CT2006'], alpha=0.85)
    ax2.bar(x + width/2, ct18_ms, width, label='CT2018', color=COLORS['CT2018'], alpha=0.85)
    ax2.set_xticks(list(x))
    ax2.set_xticklabels(r_labels, fontsize=9)
    ax2.set_ylabel('Mean Toan score')
    ax2.legend()
    ax2.grid(axis='y', alpha=0.3)
    for i, (m6, m8) in enumerate(zip(ct06_ms, ct18_ms)):
        ax2.text(i - width/2, m6 + 0.02, f'{m6:.2f}', ha='center', fontsize=8)
        ax2.text(i + width/2, m8 + 0.02, f'{m8:.2f}', ha='center', fontsize=8)

    fig.tight_layout()
    fig.savefig(f'{OUT}/hte_curriculum_by_tier.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved hte_curriculum_by_tier.png")

# ── FIG 4: bootstrap_did.png ─────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
fig.suptitle('Bootstrap DiD — Urban vs Rural COVID Recovery (2021→2024)',
             fontweight='bold', fontsize=13)

ax = axes[0]
ax.set_title('Bootstrap Distribution of DiD Estimate (1,000 iters)', fontsize=11)
ax.hist(boot_arr, bins=60, color='#457b9d', alpha=0.75, edgecolor='white', linewidth=0.3)
ax.axvline(did_point, color='#e63946', linewidth=2.5,
           label=f'Point est: {did_point:+.4f}')
ax.axvline(boot_mean, color='black',   linewidth=1.5, linestyle='--',
           label=f'Boot mean: {boot_mean:+.4f}')
ax.axvline(boot_ci_lo, color='gray', linewidth=1.5, linestyle=':',
           label=f'95% CI: [{boot_ci_lo:+.3f}, {boot_ci_hi:+.3f}]')
ax.axvline(boot_ci_hi, color='gray', linewidth=1.5, linestyle=':')
ax.axvline(0, color='orange', linewidth=1.2, linestyle='-', alpha=0.7, label='Zero')
ax.set_xlabel('DiD Estimate (Urban - Rural recovery)')
ax.set_ylabel('Frequency')
ax.legend(fontsize=8)
ax.grid(alpha=0.3)

ax2 = axes[1]
ax2.set_title('Parallel Trends: Mean Toan by Year & Tier', fontsize=11)
years_did = [2021, 2024]
all_did = pd.concat([df21, df24], ignore_index=True)
for tier, col in [('Đô thị lớn', COLORS['urban']), ('Tỉnh lẻ/Nông thôn', COLORS['rural'])]:
    means_by_year = [
        all_did[(all_did['year']==y) & (all_did['urban_tier']==tier)]['toan'].mean()
        for y in years_did
    ]
    label = tier.replace('Tỉnh lẻ/Nông thôn', 'Tinh le/NT').replace('Đô thị lớn', 'Do thi lon')
    ax2.plot(years_did, means_by_year, 'o-', color=col, label=label, linewidth=2.5, markersize=8)
    for y, m in zip(years_did, means_by_year):
        ax2.annotate(f'{m:.3f}', (y, m), textcoords='offset points',
                     xytext=(0, 8), ha='center', fontsize=9)
ax2.set_xlabel('Year')
ax2.set_ylabel('Mean Toan score')
ax2.set_xticks(years_did)
ax2.legend()
ax2.grid(alpha=0.3)

fig.tight_layout()
fig.savefig(f'{OUT}/bootstrap_did.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"  Saved bootstrap_did.png")


# ══════════════════════════════════════════════════════════════════════════════
# FINAL SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("CAUSAL ML — FINAL SUMMARY")
print("="*70)

print(f"""
ANALYSIS 1 — RDD (Curriculum Effect on Toan):
  Within-2025 (CT2018 vs CT2006):
    Raw diff = {raw_diff:+.4f}
    ATE      = {treat_coef:+.4f}  [95% CI: {treat_ci_lo:+.4f}, {treat_ci_hi:+.4f}]
    p-value  = {treat_p:.3e}
  Year-level RDD (2025-CT2018 vs 2024-CT2006):
    ATE      = {yr_coef:+.4f}  [95% CI: {yr_ci_lo:+.4f}, {yr_ci_hi:+.4f}]
    p-value  = {yr_p:.3e}

ANALYSIS 2 — Double ML (Urban Causal Effect on Toan, 2021-2024):
  Naive OLS:  {ols_ate:+.4f}  [95% CI: {ols_ate_ci_lo:+.4f}, {ols_ate_ci_hi:+.4f}]
  Double ML:  {dml_ate:+.4f}  [95% CI: {dml_ci_lo:+.4f}, {dml_ci_hi:+.4f}]
  Debiasing:  OLS overstates by {ols_ate - dml_ate:+.4f} points

ANALYSIS 3 — HTE (CT2018 effect by tier):""")

for r in hte_results:
    sig = "***" if r['p'] < 0.001 else ("**" if r['p'] < 0.01 else ("*" if r['p'] < 0.05 else "ns"))
    print(f"  {r['tier']:25s}: ATE={r['coef']:+.4f}  p={r['p']:.3e}  {sig}")

print(f"""
ANALYSIS 4 — Bootstrap DiD (Urban vs Rural, 2021→2024):
  Point estimate:  {did_point:+.4f}
  Bootstrap mean:  {boot_mean:+.4f}  (std={boot_std:.4f})
  95% CI:          [{boot_ci_lo:+.4f}, {boot_ci_hi:+.4f}]
  Significant:     {'YES' if sig_did else 'NO'}

Figures saved to: {OUT}/
  rdd_curriculum_effect.png
  dml_urban_effect.png
  hte_curriculum_by_tier.png
  bootstrap_did.png
""")
