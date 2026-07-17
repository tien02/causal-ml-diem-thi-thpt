"""
Synthetic Control + EconML + Monte Carlo Sensitivity
=====================================================
Standalone script (no importers). Run: python3 synthetic_control.py
User instruction: "keep going"

Analyses:
  1. Synthetic Control Method — province panel, CT2018 counterfactual
  2. EconML LinearDML + CausalForestDML — CATE by urban tier
  3. Rosenbaum Bounds + Monte Carlo sensitivity
  4. In-time placebo falsification
"""

import os
import sys
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats
from scipy.stats import norm, wilcoxon
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings('ignore')

sys.path.insert(0, '/home/tienda/WorkSpace/HCMUS/PTDLTM')
from province_mapping import (
    PROVINCE_NAMES_OLD as PROVINCE_NAMES,
    CHUYEN_STRONG_OLD as CHUYEN_STRONG,
    CHUYEN_STRONG_2026,
    OLD_TO_NEW_2026,
    urban_tier_old, urban_tier_2026,
    get_name_2026,
)

OUT  = '/home/tienda/WorkSpace/HCMUS/PTDLTM/figures'
BASE = '/home/tienda/WorkSpace/HCMUS/PTDLTM/GraduationExamScoreProcessing/Results'
os.makedirs(OUT, exist_ok=True)

ECONML_AVAILABLE = False
try:
    from econml.dml import LinearDML, CausalForestDML
    ECONML_AVAILABLE = True
    print("econml available — LinearDML + CausalForestDML enabled")
except ImportError:
    print("econml not available — skipping EconML section")

plt.rcParams.update({
    'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11,
    'figure.dpi': 150, 'axes.spines.top': False, 'axes.spines.right': False,
})


# ─────────────────────────────────────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────────────────────────────────────

def _rename(df: pd.DataFrame) -> pd.DataFrame:
    rmap = {
        'ngu_van': 'nguvan', 'ngoai_ngu': 'ngoaingu',
        'vat_ly': 'vatly',   'hoa_hoc': 'hoahoc',
        'sinh_hoc': 'sinhhoc', 'lich_su': 'lichsu', 'dia_ly': 'dialy',
        'vat_li': 'vatly',   'dia_li': 'dialy',
        'van': 'nguvan', 'ly': 'vatly', 'hoa': 'hoahoc',
        'sinh': 'sinhhoc', 'su': 'lichsu', 'dia': 'dialy', 'ktpl': 'gdcd',
    }
    df.columns = df.columns.str.lower().str.strip()
    return df.rename(columns={k: v for k, v in rmap.items() if k in df.columns})


def _load(path, sep=',', sbd_col='sbd', year=0, curriculum=None, treatment=None):
    df = pd.read_csv(path, sep=sep, dtype={sbd_col: str}, encoding='utf-8-sig')
    df = _rename(df)
    sbd_col = sbd_col.lower()   # _rename lowercases all columns
    if 'id' in df.columns and sbd_col not in df.columns:
        df = df.rename(columns={'id': 'sbd'})
        sbd_col = 'sbd'
    df['province_raw'] = df[sbd_col].str[:2].apply(
        lambda x: int(x) if isinstance(x, str) and x.isdigit() else np.nan)
    df['year'] = year
    if curriculum:
        df['curriculum'] = curriculum
    if treatment is not None:
        df['treatment'] = treatment
    return df


def _enrich_old(df):
    for col in ['toan', 'nguvan', 'ngoaingu']:
        df[col] = pd.to_numeric(df.get(col, np.nan), errors='coerce') if col in df.columns else np.nan
    df['province_harmonized'] = df['province_raw'].map(OLD_TO_NEW_2026).astype('Int64')
    df['urban_tier'] = df['province_raw'].apply(
        lambda p: urban_tier_old(int(p)) if pd.notna(p) else 'Unknown')
    df['is_chuyen'] = df['province_raw'].apply(
        lambda p: int(p) in CHUYEN_STRONG if pd.notna(p) else False)
    return df


def _enrich_2026(df):
    for col in ['toan', 'nguvan', 'ngoaingu']:
        df[col] = pd.to_numeric(df.get(col, np.nan), errors='coerce') if col in df.columns else np.nan
    df['province_harmonized'] = df['province_raw'].astype('Int64')
    df['urban_tier'] = df['province_raw'].apply(
        lambda p: urban_tier_2026(int(p)) if pd.notna(p) else 'Unknown')
    df['is_chuyen'] = df['province_raw'].apply(
        lambda p: int(p) in CHUYEN_STRONG_2026 if pd.notna(p) else False)
    return df


print("Loading data...")
df21     = _enrich_old(_load(f'{BASE}/Diemthi2021.csv', sbd_col='SBD',
                              year=2021, curriculum='CT2006'))
df22     = _enrich_old(_load(f'{BASE}/Diemthi2022.csv',
                              year=2022, curriculum='CT2006'))
df24     = _enrich_old(_load(f'{BASE}/2024/Diemthi2024.csv',
                              year=2024, curriculum='CT2006'))
df25_old = _enrich_old(_load(f'{BASE}/2025/20250715-ketquathi-ct2006.csv',
                              sep=';', year=2025, curriculum='CT2006', treatment=0))
df25_new = _enrich_old(_load(f'{BASE}/2025/20250715-ketquathi-ct2018a.csv',
                              sep=';', year=2025, curriculum='CT2018', treatment=1))
df26     = _enrich_2026(_load(f'{BASE}/2026/diemthithpt_2026.csv',
                               sbd_col='id', year=2026, curriculum='CT2018', treatment=1))

for label, df in [('2021', df21), ('2022', df22), ('2024', df24),
                  ('2025-CT2006', df25_old), ('2025-CT2018', df25_new), ('2026', df26)]:
    print(f"  {label}: {len(df):,} rows, {df['toan'].notna().sum():,} with Toán")


# ─────────────────────────────────────────────────────────────────────────────
# PROVINCE PANEL: mean Toán per province_harmonized per year/cohort
# ─────────────────────────────────────────────────────────────────────────────

def build_panel():
    frames = []
    for df, year, cohort in [
        (df21, 2021, 'CT2006'), (df22, 2022, 'CT2006'), (df24, 2024, 'CT2006'),
        (df25_old, 2025, 'CT2006'), (df25_new, 2025, 'CT2018'),
    ]:
        g = (df[df['toan'].notna()]
             .groupby('province_harmonized')
             .agg(mean_toan=('toan', 'mean'), n=('toan', 'count'),
                  urban_tier=('urban_tier', 'first'), is_chuyen=('is_chuyen', 'first'))
             .reset_index())
        g['year'] = year
        g['cohort'] = cohort
        frames.append(g)
    p = pd.concat(frames, ignore_index=True)
    p['prov_name'] = p['province_harmonized'].apply(
        lambda x: get_name_2026(int(x)) if pd.notna(x) else 'Unknown')
    return p


print("\nBuilding province panel...")
panel = build_panel()
print(f"  {len(panel)} province-year rows, {panel['province_harmonized'].nunique()} provinces")


# ══════════════════════════════════════════════════════════════════════════════
# 1. SYNTHETIC CONTROL METHOD
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("ANALYSIS 1: SYNTHETIC CONTROL")
print("="*70)

pre_panel = panel[(panel['year'].isin([2021, 2022, 2024])) & (panel['cohort'] == 'CT2006')]
post_2025  = panel[(panel['year'] == 2025) & (panel['cohort'] == 'CT2018')]

full_pre = (pre_panel.groupby('province_harmonized')['year']
            .count().loc[lambda s: s == 3].index)
valid_provs = full_pre[full_pre.isin(post_2025['province_harmonized'].values)]
print(f"Provinces with full pre-trend + 2025 CT2018: {len(valid_provs)}")

sc_rows = []
for prov in valid_provs:
    pre_p  = pre_panel[pre_panel['province_harmonized'] == prov].sort_values('year')
    post_p = post_2025[post_2025['province_harmonized'] == prov]
    if post_p.empty:
        continue
    reg = LinearRegression()
    reg.fit(pre_p['year'].values.reshape(-1, 1), pre_p['mean_toan'].values)
    synth25 = float(reg.predict([[2025]])[0])
    actual  = float(post_p['mean_toan'].values[0])
    sc_rows.append({
        'province_harmonized': prov,
        'prov_name':    pre_p['prov_name'].values[0],
        'urban_tier':   pre_p['urban_tier'].values[0],
        'is_chuyen':    pre_p['is_chuyen'].values[0],
        'actual_2025':  actual,
        'synth_2025':   synth25,
        'gap':          actual - synth25,
        'n':            int(post_p['n'].values[0]),
        'slope':        float(reg.coef_[0]),
    })

sc_df = pd.DataFrame(sc_rows)
sc_df['weight'] = sc_df['n'] / sc_df['n'].sum()

national_ate = float((sc_df['gap'] * sc_df['weight']).sum())
se_gap = float(np.sqrt(((sc_df['gap'] - national_ate)**2 * sc_df['weight']).sum()))
ci_lo  = national_ate - 1.96 * se_gap / np.sqrt(len(sc_df))
ci_hi  = national_ate + 1.96 * se_gap / np.sqrt(len(sc_df))

print(f"\nNational ATE : {national_ate:+.3f} pts")
print(f"95% CI       : [{ci_lo:+.3f}, {ci_hi:+.3f}]")

for tier in ['Đô thị lớn', 'Đô thị vừa', 'Tỉnh lẻ/Nông thôn']:
    sub = sc_df[sc_df['urban_tier'] == tier]
    if sub.empty:
        continue
    w = float((sub['gap'] * sub['n']).sum() / sub['n'].sum())
    print(f"  {tier}: {w:+.3f} (n={len(sub)})")

# Placebo: predict 2024 from 2021+2022
plac_rows = []
for prov in valid_provs:
    p2 = pre_panel[(pre_panel['province_harmonized'] == prov) &
                   (pre_panel['year'].isin([2021, 2022]))].sort_values('year')
    a24 = pre_panel[(pre_panel['province_harmonized'] == prov) &
                    (pre_panel['year'] == 2024)]
    if len(p2) < 2 or a24.empty:
        continue
    reg2 = LinearRegression()
    reg2.fit(p2['year'].values.reshape(-1, 1), p2['mean_toan'].values)
    plac_rows.append({
        'gap': float(a24['mean_toan'].values[0]) - float(reg2.predict([[2024]])[0]),
        'n':   int(a24['n'].values[0]),
    })
plac_df  = pd.DataFrame(plac_rows)
plac_ate = float((plac_df['gap'] * plac_df['n']).sum() / plac_df['n'].sum())
plac_se  = float(np.std(plac_df['gap']) / np.sqrt(len(plac_df)))
t_plac   = abs(plac_ate / plac_se) if plac_se > 0 else 0.0
print(f"\nPlacebo 2024 gap: {plac_ate:+.3f} ± {plac_se:.3f}  |t|={t_plac:.2f}  "
      f"({'HOLDS' if t_plac < 1.96 else 'FAILS'} parallel trends)")

# Permutation
rng = np.random.default_rng(42)
gaps_arr = sc_df['gap'].values
wts = sc_df['weight'].values
perm_ates = np.array([(rng.permutation(gaps_arr) * wts).sum() for _ in range(2000)])
perm_p = float(np.mean(np.abs(perm_ates) >= abs(national_ate)))
print(f"Permutation p : {perm_p:.4f}")

# ── Fig 1: trajectory + province gaps ─────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

ax = axes[0]
nat_pre_pts = [(yr, float((pre_panel[pre_panel['year'] == yr]['mean_toan'] *
                            pre_panel[pre_panel['year'] == yr]['n']).sum() /
                           pre_panel[pre_panel['year'] == yr]['n'].sum()))
               for yr in [2021, 2022, 2024]]
ys_pre = [v for _, v in nat_pre_pts]
xs_pre = [yr for yr, _ in nat_pre_pts]
post_act  = float((post_2025['mean_toan'] * post_2025['n']).sum() / post_2025['n'].sum())
post_synth = float((sc_df['synth_2025'] * sc_df['n']).sum() / sc_df['n'].sum())

ax.plot(xs_pre, ys_pre, 'o-', color='#2176AE', lw=2, label='Actual (CT2006 pre-treatment)')
ax.plot(xs_pre + [2025], ys_pre + [post_synth], 's--', color='#888', lw=1.5, alpha=0.7,
        label='Synthetic (linear trend)')
ax.plot(2025, post_act,   '^', color='#D62828', ms=12, zorder=5,
        label=f'Actual CT2018 2025 ({post_act:.3f})')
ax.plot(2025, post_synth, 's', color='#888',    ms=10, zorder=5)
ax.annotate(f'Gap={national_ate:+.3f}\n95%CI [{ci_lo:+.2f},{ci_hi:+.2f}]\np={perm_p:.3f}',
            xy=(2025, (post_act + post_synth) / 2),
            xytext=(2023.3, (post_act + post_synth) / 2 + 0.07),
            fontsize=8.5, color='#D62828',
            arrowprops=dict(arrowstyle='->', color='#D62828'))
ax.axvline(2024.5, ls=':', color='gray', alpha=0.5)
ax.text(2024.55, min(ys_pre) - 0.05, 'CT2018\nstart', fontsize=8, color='gray')
ax.set_xticks([2021, 2022, 2024, 2025])
ax.set_xlabel('Year')
ax.set_ylabel('Mean Toán (national, n-weighted)')
ax.set_title('Synthetic Control — CT2018 Counterfactual (Toán)')
ax.legend(fontsize=9)

ax = axes[1]
sc_s = sc_df.sort_values('gap')
bar_c = ['#D62828' if g < 0 else '#2176AE' for g in sc_s['gap']]
ax.barh(range(len(sc_s)), sc_s['gap'], color=bar_c, alpha=0.85)
ax.axvline(national_ate, color='black', ls='--', lw=1.5,
           label=f'ATE = {national_ate:+.3f}')
ax.axvline(0, color='gray', lw=0.8, alpha=0.4)
ax.set_yticks(range(len(sc_s)))
ax.set_yticklabels(sc_s['prov_name'], fontsize=6.5)
ax.set_xlabel('Gap: Actual CT2018 − Synthetic [pts]')
ax.set_title('Province-Level SC Gaps')
ax.legend(fontsize=9)

plt.tight_layout()
plt.savefig(f'{OUT}/sc_main.png', bbox_inches='tight', dpi=150)
plt.close()
print("\nSaved: sc_main.png")

# ── Fig 2: permutation ─────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 4))
ax.hist(perm_ates, bins=60, color='#adb5bd', edgecolor='white', alpha=0.8)
ax.axvline(national_ate, color='#D62828', lw=2, label=f'Observed ATE = {national_ate:+.3f}')
ax.axvline(np.percentile(perm_ates, 2.5),  color='gray', ls='--', lw=1)
ax.axvline(np.percentile(perm_ates, 97.5), color='gray', ls='--', lw=1,
           label='95% permutation CI')
ax.set_xlabel('Permuted national ATE')
ax.set_ylabel('Count')
ax.set_title(f'Permutation Test (n=2000), p = {perm_p:.4f}')
ax.legend()
plt.tight_layout()
plt.savefig(f'{OUT}/sc_permutation.png', bbox_inches='tight', dpi=150)
plt.close()
print("Saved: sc_permutation.png")


# ══════════════════════════════════════════════════════════════════════════════
# 2. ECONML — LinearDML + CausalForestDML
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("ANALYSIS 2: ECONML")
print("="*70)

ate_linear = ate_forest = None

if ECONML_AVAILABLE:
    df25 = pd.concat([df25_old, df25_new], ignore_index=True)
    d = df25[df25['toan'].notna() & df25['province_harmonized'].notna()].copy()

    d['urban_large'] = (d['urban_tier'] == 'Đô thị lớn').astype(int)
    d['urban_mid']   = (d['urban_tier'] == 'Đô thị vừa').astype(int)
    d['is_chuyen_i'] = d['is_chuyen'].astype(int)
    pn = d.groupby('province_harmonized')['toan'].count().rename('prov_n')
    d  = d.join(pn, on='province_harmonized')
    d['prov_size'] = np.log1p(d['prov_n'])

    feats = ['urban_large', 'urban_mid', 'is_chuyen_i', 'prov_size']
    Y_all, T_all = d['toan'].values, d['treatment'].values
    X_raw = d[feats].fillna(0).values
    scaler = StandardScaler()
    X_sc   = scaler.fit_transform(X_raw)

    CAP = 200_000
    rng2 = np.random.default_rng(42)
    if len(Y_all) > CAP:
        idx = rng2.choice(len(Y_all), CAP, replace=False)
        Ys, Ts, Xs, Xr = Y_all[idx], T_all[idx], X_sc[idx], X_raw[idx]
    else:
        Ys, Ts, Xs, Xr = Y_all, T_all, X_sc, X_raw

    print(f"\nLinearDML on {len(Ys):,} samples...")
    est_lin = LinearDML(
        model_y=GradientBoostingRegressor(n_estimators=100, max_depth=3, random_state=42),
        model_t=GradientBoostingRegressor(n_estimators=100, max_depth=3, random_state=42),
        discrete_treatment=True, cv=5, random_state=42,
    )
    est_lin.fit(Ys, Ts, X=Xs)
    ate_linear = float(est_lin.ate(Xs))
    print(f"  LinearDML ATE: {ate_linear:+.3f}")
    for tn, ul, um in [('Đô thị lớn', 1, 0), ('Đô thị vừa', 0, 1), ('Nông thôn', 0, 0)]:
        xq = scaler.transform([[ul, um, 0, np.log1p(50_000)]])
        print(f"    {tn}: {float(est_lin.effect(xq)):+.3f}")

    print(f"\nCausalForestDML on {len(Ys):,} samples...")
    est_cf = CausalForestDML(
        n_estimators=200, min_samples_leaf=50, max_depth=4,
        discrete_treatment=True, cv=3, random_state=42, n_jobs=-1,
    )
    est_cf.fit(Ys, Ts, X=Xs)
    cate_preds = est_cf.effect(Xs)
    ate_forest = float(np.mean(cate_preds))
    print(f"  CausalForest ATE: {ate_forest:+.3f}")
    print(f"  CATE p5/p95: [{np.percentile(cate_preds,5):.3f}, {np.percentile(cate_preds,95):.3f}]")

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    ax = axes[0]
    ax.hist(cate_preds, bins=80, color='#2176AE', alpha=0.8, edgecolor='white')
    ax.axvline(ate_forest, color='#D62828', lw=2, label=f'ATE = {ate_forest:.3f}')
    ax.axvline(0, color='gray', ls='--', lw=1, alpha=0.6)
    ax.set_xlabel('Individual CATE (CT2018 Toán effect)')
    ax.set_ylabel('Count')
    ax.set_title('CausalForestDML: CATE Distribution\n(2025 CT2018 vs CT2006)')
    ax.legend()

    ax = axes[1]
    dc = pd.DataFrame(Xr, columns=feats)
    dc['cate'] = cate_preds
    dc['tier'] = dc.apply(
        lambda r: 'Đô thị lớn' if r['urban_large'] == 1
        else ('Đô thị vừa' if r['urban_mid'] == 1 else 'Nông thôn'), axis=1)
    tiers_v  = ['Đô thị lớn', 'Đô thị vừa', 'Nông thôn']
    cols_v   = ['#2176AE', '#F4A261', '#6a994e']
    parts = ax.violinplot(
        [dc[dc['tier'] == t]['cate'].values for t in tiers_v],
        positions=range(3), showmedians=True, showextrema=False,
    )
    for pc, col in zip(parts['bodies'], cols_v):
        pc.set_facecolor(col); pc.set_alpha(0.75)
    ax.set_xticks(range(3))
    ax.set_xticklabels(tiers_v)
    ax.axhline(ate_forest, color='#D62828', ls='--', lw=1.2,
               label=f'ATE = {ate_forest:.3f}')
    ax.axhline(0, color='gray', lw=0.8, alpha=0.4)
    ax.set_ylabel('CATE')
    ax.set_title('CT2018 CATE by Urban Tier (CausalForest)')
    ax.legend(fontsize=9)
    plt.tight_layout()
    plt.savefig(f'{OUT}/econml_cate.png', bbox_inches='tight', dpi=150)
    plt.close()
    print("Saved: econml_cate.png")
else:
    print("  econml unavailable — skipped")


# ══════════════════════════════════════════════════════════════════════════════
# 3. ROSENBAUM BOUNDS + MONTE CARLO
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("ANALYSIS 3: ROSENBAUM BOUNDS + MONTE CARLO")
print("="*70)

gaps   = sc_df['gap'].values
ranks  = stats.rankdata(np.abs(gaps))
stat_w, p_w = wilcoxon(gaps, alternative='two-sided')
print(f"Wilcoxon: stat={stat_w:.1f}, p={p_w:.4f}")

gamma_range = np.arange(1.0, 6.05, 0.1)
p_upper = []
for g in gamma_range:
    pi  = g / (1 + g)
    e   = pi * np.sum(ranks)
    v   = pi * (1 - pi) * np.sum(ranks**2)
    z   = (stat_w - e) / np.sqrt(v)
    p_upper.append(max(0.0, float(2 * norm.cdf(-abs(z)))))
p_upper = np.array(p_upper)

over_idx = np.where(p_upper > 0.05)[0]
gamma_star = float(gamma_range[over_idx[0]]) if len(over_idx) > 0 else float(gamma_range[-1])
print(f"Rosenbaum Γ* = {gamma_star:.1f}x  (confounder needed to overturn)")

GAMMA_MC = 2.0
rng_mc = np.random.default_rng(123)
mc_ates = np.array([
    float(np.mean(gaps + rng_mc.uniform(-np.log(GAMMA_MC), np.log(GAMMA_MC), len(gaps)) * 0.15))
    for _ in range(5000)
])
frac_neg = float(np.mean(mc_ates < 0))
mc_p05, mc_p95 = float(np.percentile(mc_ates, 5)), float(np.percentile(mc_ates, 95))
robust_str = 'ROBUST' if frac_neg > 0.9 else f'SENSITIVE at Γ={GAMMA_MC}'
print(f"MC Γ={GAMMA_MC}: 90% range [{mc_p05:.3f}, {mc_p95:.3f}], neg={frac_neg:.1%} → {robust_str}")

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
ax = axes[0]
ax.plot(gamma_range, p_upper, 'o-', color='#2176AE', lw=2, ms=4, label='Worst-case p-value')
ax.axhline(0.05, color='#D62828', ls='--', lw=1.5, label='α = 0.05')
ax.axvline(gamma_star, color='#F4A261', ls='--', lw=1.5, label=f'Γ* = {gamma_star:.1f}')
ax.fill_between(gamma_range, p_upper, 0.05, where=p_upper <= 0.05,
                alpha=0.15, color='#2176AE', label='Significant zone')
ax.set_xlabel('Γ (hidden confounder odds ratio)')
ax.set_ylabel('Worst-case p-value (Rosenbaum bound)')
ax.set_title('Sensitivity Bounds — CT2018 Toán Effect\n(Province-level SC gaps)')
ax.legend(fontsize=9)
ax.set_ylim(0, min(1.0, max(p_upper) * 1.1 + 0.05))

ax = axes[1]
ax.hist(mc_ates, bins=60, color='#2176AE', alpha=0.8, edgecolor='white')
ax.axvline(national_ate, color='black', lw=2, label=f'Observed ATE = {national_ate:.3f}')
ax.axvline(mc_p05, color='#D62828', ls='--', lw=1.5, label='90% MC interval')
ax.axvline(mc_p95, color='#D62828', ls='--', lw=1.5)
ax.axvline(0, color='gray', ls=':', lw=1)
ax.set_xlabel(f'ATE under Γ={GAMMA_MC} hidden confounder (MC n=5000)')
ax.set_ylabel('Count')
ax.set_title(f'Monte Carlo Sensitivity (Γ={GAMMA_MC})\n{frac_neg:.1%} negative → {robust_str}')
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig(f'{OUT}/mc_sensitivity.png', bbox_inches='tight', dpi=150)
plt.close()
print("Saved: mc_sensitivity.png")


# ══════════════════════════════════════════════════════════════════════════════
# SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print(f"SC national ATE  : {national_ate:+.3f} [{ci_lo:+.3f}, {ci_hi:+.3f}]  p={perm_p:.4f}")
print(f"Placebo 2024     : {plac_ate:+.3f} ± {plac_se:.3f}  (parallel trends "
      f"{'HOLDS' if t_plac < 1.96 else 'FAILS'})")
print(f"Rosenbaum Γ*     : {gamma_star:.1f}x")
print(f"MC Γ=2 negative  : {frac_neg:.1%}  → {robust_str}")
if ECONML_AVAILABLE and ate_linear is not None:
    print(f"LinearDML ATE    : {ate_linear:+.3f}")
    print(f"CausalForest ATE : {ate_forest:+.3f}")
print("\nFigures:")
for fn in ['sc_main.png', 'sc_permutation.png', 'mc_sensitivity.png', 'econml_cate.png']:
    fp = f'{OUT}/{fn}'
    if os.path.exists(fp):
        print(f"  {fn} ({os.path.getsize(fp)//1024} KB)")
