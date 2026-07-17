"""
Fraud Anomaly Detection — Vietnam 2026 University Entrance Exam
===============================================================
Uses harmonized panel of 2021/2022/2024/2026 Math scores to detect
provinces whose 2026 results are statistically anomalous relative to
their own historical trend.

Detection layers
----------------
1. Trend residual (linear regression per province, Z-score residuals)
2. Distribution shape divergence (KL divergence vs 2024)
3. Low within-province variance (possible score uniformisation)

2018 fraud provinces mapped to new 2026 codes: {4, 14}
"""

import os
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy import stats
from scipy.special import rel_entr
from sklearn.linear_model import LinearRegression
warnings.filterwarnings('ignore')

from province_mapping import (
    OLD_TO_NEW_2026,
    PROVINCE_DISPLAY_2026,
    FRAUD_ADJACENT_2026,
)

# ─────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────
BASE = '/home/tienda/WorkSpace/HCMUS/PTDLTM/GraduationExamScoreProcessing/Results'
OUT  = '/home/tienda/WorkSpace/HCMUS/PTDLTM/figures'
os.makedirs(OUT, exist_ok=True)

# ─────────────────────────────────────────────
# Data loading (copied from analysis.py pattern)
# ─────────────────────────────────────────────

def load_2021():
    df = pd.read_csv(f'{BASE}/Diemthi2021.csv', dtype={'SBD': str, 'Cum_thi': str})
    df.columns = df.columns.str.lower().str.strip()
    df['province_old'] = df['cum_thi'].str.zfill(2).str[:2].apply(
        lambda x: int(x) if x.isdigit() else np.nan)
    df['toan'] = pd.to_numeric(df.get('toan', np.nan), errors='coerce')
    df['year'] = 2021
    return df[['province_old', 'toan', 'year']]

def load_2022():
    df = pd.read_csv(f'{BASE}/Diemthi2022.csv', dtype={'sbd': str})
    df.columns = df.columns.str.lower().str.strip()
    df['province_old'] = df['sbd'].str[:2].apply(lambda x: int(x) if x.isdigit() else np.nan)
    df['toan'] = pd.to_numeric(df.get('toan', np.nan), errors='coerce')
    df['year'] = 2022
    return df[['province_old', 'toan', 'year']]

def load_2024():
    df = pd.read_csv(f'{BASE}/2024/Diemthi2024.csv', dtype={'sbd': str})
    df.columns = df.columns.str.lower().str.strip()
    df['province_old'] = df['sbd'].str[:2].apply(lambda x: int(x) if x.isdigit() else np.nan)
    df['toan'] = pd.to_numeric(df.get('toan', np.nan), errors='coerce')
    df['year'] = 2024
    return df[['province_old', 'toan', 'year']]

def load_2026():
    df = pd.read_csv(f'{BASE}/2026/diemthithpt_2026.csv', dtype={'id': str})
    df.columns = df.columns.str.lower().str.strip()
    df['province'] = df['id'].str[:2].apply(lambda x: int(x) if x.isdigit() else np.nan)
    df['toan'] = pd.to_numeric(df.get('toan', np.nan), errors='coerce')
    df['year'] = 2026
    return df[['province', 'toan', 'year']]

# ─────────────────────────────────────────────
# Step 1: Build harmonized panel
# ─────────────────────────────────────────────
print("=" * 70)
print("FRAUD ANOMALY DETECTION — VIETNAM 2026 UNIVERSITY ENTRANCE EXAM")
print("=" * 70)

print("\nStep 1: Loading data...")

df21 = load_2021()
df22 = load_2022()
df24 = load_2024()
df26 = load_2026()

print(f"  2021: {len(df21):,} rows  |  toan non-null: {df21['toan'].notna().sum():,}")
print(f"  2022: {len(df22):,} rows  |  toan non-null: {df22['toan'].notna().sum():,}")
print(f"  2024: {len(df24):,} rows  |  toan non-null: {df24['toan'].notna().sum():,}")
print(f"  2026: {len(df26):,} rows  |  toan non-null: {df26['toan'].notna().sum():,}")

# Map old province codes to new 2026 codes for historical years
for df in [df21, df22, df24]:
    df['province'] = df['province_old'].map(OLD_TO_NEW_2026)

# Province-year means for historical years (CT2006 curriculum)
hist_frames = []
for df, year in [(df21, 2021), (df22, 2022), (df24, 2024)]:
    means = (
        df.dropna(subset=['province', 'toan'])
        .groupby('province')['toan']
        .agg(mean='mean', std='std', n='count')
        .reset_index()
    )
    means['year'] = year
    hist_frames.append(means)

hist = pd.concat(hist_frames, ignore_index=True)

# 2026 province means
prov26 = (
    df26.dropna(subset=['province', 'toan'])
    .groupby('province')['toan']
    .agg(mean='mean', std='std', n='count')
    .reset_index()
    .rename(columns={'mean': 'actual_2026', 'std': 'std_2026', 'n': 'n_2026'})
)

print(f"\n  Historical panel: {len(hist)} province-year observations")
print(f"  2026 provinces with math data: {len(prov26)}")

# ─────────────────────────────────────────────
# Step 2: Trend-based expected score via linear regression
# ─────────────────────────────────────────────
print("\nStep 2: Fitting per-province linear trends (score ~ year)...")

provinces_2026 = sorted(prov26['province'].dropna().unique().astype(int).tolist())

trend_results = []

for prov in provinces_2026:
    prov_hist = hist[hist['province'] == prov].dropna(subset=['mean'])
    n_obs = len(prov_hist)

    actual_row = prov26.loc[prov26['province'] == prov, 'actual_2026'].values
    actual_val = float(actual_row[0]) if len(actual_row) > 0 else np.nan

    if n_obs < 2:
        # Not enough history — use single available observation as the expectation
        if n_obs == 1:
            expected = float(prov_hist['mean'].values[0])
            note = 'single-obs extrapolation'
        else:
            expected = np.nan
            note = 'no history'
        trend_results.append({
            'province': prov,
            'n_hist_obs': n_obs,
            'actual_2026': actual_val,
            'expected_2026': expected,
            'note': note,
        })
        continue

    # Fit OLS: mean ~ year
    X = prov_hist['year'].values.reshape(-1, 1)
    y = prov_hist['mean'].values
    reg = LinearRegression().fit(X, y)
    expected = float(np.clip(reg.predict([[2026]])[0], 0.0, 10.0))

    trend_results.append({
        'province': prov,
        'n_hist_obs': n_obs,
        'actual_2026': actual_val,
        'expected_2026': expected,
        'note': 'ok',
    })

trend_df = pd.DataFrame(trend_results)
trend_df['residual'] = trend_df['actual_2026'] - trend_df['expected_2026']

# Z-score residuals across all provinces
valid_mask = trend_df['residual'].notna()
res_mean = trend_df.loc[valid_mask, 'residual'].mean()
res_std  = trend_df.loc[valid_mask, 'residual'].std()
trend_df['z_score'] = (trend_df['residual'] - res_mean) / res_std

print(f"  Residual mean: {res_mean:.4f}, std: {res_std:.4f}")
print(f"  Z-score range: [{trend_df['z_score'].min():.2f}, {trend_df['z_score'].max():.2f}]")

# ─────────────────────────────────────────────
# Step 3: KL divergence on score distribution shape
# ─────────────────────────────────────────────
print("\nStep 3: Computing KL divergence (2026 vs 2024 distribution shape)...")

BINS = np.linspace(0, 10, 41)  # 40 equal bins of width 0.25

def province_hist_normalized(df_raw, province_col, prov_code, bins):
    """Return normalized probability distribution over score bins for a province."""
    scores = df_raw.loc[df_raw[province_col] == prov_code, 'toan'].dropna()
    if len(scores) < 50:
        return None
    counts, _ = np.histogram(scores, bins=bins)
    total = counts.sum()
    if total == 0:
        return None
    return counts / total

def safe_kl(p, q, eps=1e-10):
    """KL(p || q) with Laplace smoothing to avoid division by zero."""
    p = np.asarray(p, dtype=float) + eps
    q = np.asarray(q, dtype=float) + eps
    p /= p.sum()
    q /= q.sum()
    return float(np.sum(rel_entr(p, q)))

# Map 2024 data to new province codes for comparison
df24_mapped = df24.copy()
df24_mapped['province_new'] = df24_mapped['province_old'].map(OLD_TO_NEW_2026)

kl_results = []
for prov in provinces_2026:
    p26 = province_hist_normalized(df26, 'province', prov, BINS)
    p24 = province_hist_normalized(df24_mapped, 'province_new', prov, BINS)
    if p26 is None or p24 is None:
        kl_results.append({'province': prov, 'kl_divergence': np.nan})
        continue
    kl = safe_kl(p26, p24)
    kl_results.append({'province': prov, 'kl_divergence': kl})

kl_df = pd.DataFrame(kl_results)

# ─────────────────────────────────────────────
# Step 4: Low-variance check
# ─────────────────────────────────────────────
print("\nStep 4: Within-province standard deviation analysis...")

std_df = prov26[['province', 'std_2026', 'n_2026']].copy()
trend_df = trend_df.merge(std_df, on='province', how='left')

valid_std_mask = trend_df['std_2026'].notna()
std_mean = trend_df.loc[valid_std_mask, 'std_2026'].mean()
std_std  = trend_df.loc[valid_std_mask, 'std_2026'].std()
trend_df['std_z'] = (trend_df['std_2026'] - std_mean) / std_std

print(f"  Within-province std mean: {std_mean:.4f}, std of stds: {std_std:.4f}")

# ─────────────────────────────────────────────
# Step 5: Assemble output table
# ─────────────────────────────────────────────
print("\nStep 5: Assembling fraud flags...")

report = trend_df.merge(kl_df, on='province', how='left')

report['province_name'] = report['province'].apply(
    lambda p: PROVINCE_DISPLAY_2026.get(int(p), f'Unknown({int(p)})') if pd.notna(p) else 'Unknown'
)

Z_THRESHOLD  = 2.0
KL_THRESHOLD = report['kl_divergence'].quantile(0.75)  # top quartile KL divergence

report['flag_trend']    = report['z_score'] > Z_THRESHOLD
report['flag_kl_shift'] = (
    (report['kl_divergence'] > KL_THRESHOLD) &
    (report['residual'] > 0)
)
report['flag_low_var']  = report['std_z'] < -Z_THRESHOLD

# Fraud flag: >= 2 signals OR extreme Z (> 3)
report['fraud_flag'] = (
    (report['flag_trend'].astype(int) +
     report['flag_kl_shift'].astype(int) +
     report['flag_low_var'].astype(int)) >= 2
) | (report['z_score'] > 3.0)

report['fraud_adjacent_2018'] = report['province'].isin(FRAUD_ADJACENT_2026)

report_sorted = report.sort_values(
    ['fraud_flag', 'z_score'], ascending=[False, False]
).reset_index(drop=True)

# ─────────────────────────────────────────────
# Print results
# ─────────────────────────────────────────────
print("\n" + "=" * 70)
print("RESULTS: RANKED SUSPICIOUS PROVINCES (2026 MATH ANOMALY DETECTION)")
print("=" * 70)

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 160)
pd.set_option('display.float_format', '{:.4f}'.format)

DISPLAY_COLS = [
    'province', 'province_name',
    'actual_2026', 'expected_2026', 'residual', 'z_score',
    'kl_divergence', 'std_2026', 'std_z',
    'fraud_flag', 'fraud_adjacent_2018',
    'flag_trend', 'flag_kl_shift', 'flag_low_var',
    'n_2026', 'n_hist_obs',
]
for col in DISPLAY_COLS:
    if col not in report_sorted.columns:
        report_sorted[col] = np.nan

print("\n--- ALL PROVINCES (sorted by fraud flag then Z-score) ---")
display_df = report_sorted[DISPLAY_COLS].copy()
display_df['province'] = display_df['province'].apply(lambda x: int(x) if pd.notna(x) else x)
print(display_df.to_string(index=False))

# Flagged provinces
flagged = report_sorted[report_sorted['fraud_flag'] == True]
print(f"\n{'='*70}")
print(f"FRAUD-FLAGGED PROVINCES: {len(flagged)} of {len(report_sorted)}")
print(f"{'='*70}")
if len(flagged) > 0:
    for _, row in flagged.iterrows():
        adj_marker = ' *** 2018 FRAUD-ADJACENT ***' if row['fraud_adjacent_2018'] else ''
        print(f"\n  [{int(row['province'])}] {row['province_name']}{adj_marker}")
        print(f"     actual_2026={row['actual_2026']:.3f}  expected={row['expected_2026']:.3f}  "
              f"residual={row['residual']:+.3f}  Z={row['z_score']:+.2f}")
        print(f"     KL_div={row['kl_divergence']:.4f}  std={row['std_2026']:.3f}  std_Z={row['std_z']:+.2f}")
        print(f"     Signals: trend={row['flag_trend']}  kl+shift={row['flag_kl_shift']}  low_var={row['flag_low_var']}")
        print(f"     n_2026={int(row['n_2026']) if pd.notna(row['n_2026']) else 'N/A'}")
else:
    print("  No provinces exceed the fraud flag threshold.")

# Elevated inflation risk (below full flag threshold)
inflation_risk = report_sorted[
    (report_sorted['z_score'] > 1.5) & (~report_sorted['fraud_flag'])
]
if len(inflation_risk) > 0:
    print(f"\n--- ELEVATED INFLATION RISK (1.5 < Z <= 2.0, not fully flagged) ---")
    for _, row in inflation_risk.iterrows():
        adj_marker = ' [2018 adj]' if row['fraud_adjacent_2018'] else ''
        print(f"  [{int(row['province'])}] {row['province_name']}{adj_marker}  "
              f"Z={row['z_score']:+.2f}  actual={row['actual_2026']:.3f}  expected={row['expected_2026']:.3f}")

print(f"\n{'='*70}")
print("SUMMARY STATISTICS")
print(f"{'='*70}")
print(f"  Total 2026 provinces analyzed:          {len(report_sorted)}")
print(f"  Provinces with Z > 0 (above trend):     {(report_sorted['z_score'] > 0).sum()}")
print(f"  Provinces with Z > 2 (strong anomaly):  {(report_sorted['z_score'] > Z_THRESHOLD).sum()}")
print(f"  Provinces with Z > 3 (extreme):         {(report_sorted['z_score'] > 3).sum()}")
print(f"  Provinces with low variance (std_Z<-2): {(report_sorted['std_z'] < -Z_THRESHOLD).sum()}")
print(f"  KL threshold (75th percentile):         {KL_THRESHOLD:.4f}")
print(f"\n  2018 fraud-adjacent provinces (codes 4, 14):")
for prov_code in sorted(FRAUD_ADJACENT_2026):
    row = report_sorted[report_sorted['province'] == prov_code]
    if len(row) > 0:
        r = row.iloc[0]
        print(f"    [{prov_code}] {r['province_name']}: Z={r['z_score']:+.2f}, "
              f"actual={r['actual_2026']:.3f}, fraud_flag={r['fraud_flag']}")

# ─────────────────────────────────────────────
# Figures
# ─────────────────────────────────────────────
print("\nGenerating figures...")

plt.rcParams.update({'font.size': 10})

# ── Figure 1: Z-score bar chart ───────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(20, 8))
ax.set_title(
    'Fraud Anomaly Detection: Z-score of 2026 Math Mean vs Historical Trend\n'
    '(|Z| > 2 flagged; red = positive anomaly / score inflation)',
    fontweight='bold', fontsize=12
)

plot_df = (
    report_sorted.dropna(subset=['z_score'])
    .sort_values('z_score', ascending=False)
    .reset_index(drop=True)
)
labels = [
    f"{PROVINCE_DISPLAY_2026.get(int(p), str(int(p)))}\n[{int(p)}]"
    for p in plot_df['province']
]

bar_colors = []
for _, row in plot_df.iterrows():
    if row['fraud_flag']:
        bar_colors.append('#d62728')    # dark red: fraud flagged
    elif row['z_score'] > Z_THRESHOLD:
        bar_colors.append('#ff7f0e')    # orange: above threshold only
    elif row['z_score'] < -Z_THRESHOLD:
        bar_colors.append('#1f77b4')    # blue: unusual drop
    else:
        bar_colors.append('#aec7e8')    # light blue: normal

ax.bar(range(len(plot_df)), plot_df['z_score'], color=bar_colors, alpha=0.85, edgecolor='white')
ax.axhline( Z_THRESHOLD, color='red',  linestyle='--', linewidth=1.2, label=f'+{Z_THRESHOLD}σ')
ax.axhline(-Z_THRESHOLD, color='blue', linestyle='--', linewidth=1.2, label=f'-{Z_THRESHOLD}σ')
ax.axhline(0,            color='gray', linestyle='-',  linewidth=0.8, alpha=0.5)

for i, row in plot_df.iterrows():
    if row['province'] in FRAUD_ADJACENT_2026:
        ax.annotate('2018\nadj', xy=(i, row['z_score']),
                    xytext=(i, row['z_score'] + 0.35 * np.sign(row['z_score'] + 1e-9)),
                    fontsize=7, color='darkred', ha='center', fontweight='bold')

ax.set_xticks(range(len(plot_df)))
ax.set_xticklabels(labels, fontsize=7, rotation=45, ha='right')
ax.set_ylabel('Z-score  (actual_2026 − predicted_2026) / σ', fontsize=10)
ax.set_xlabel('Province (2026 administrative code)', fontsize=10)

patches = [
    mpatches.Patch(color='#d62728', label='Fraud flagged (≥2 signals)'),
    mpatches.Patch(color='#ff7f0e', label='Above threshold only (Z > 2)'),
    mpatches.Patch(color='#aec7e8', label='Normal range (|Z| ≤ 2)'),
    mpatches.Patch(color='#1f77b4', label='Below threshold (Z < −2)'),
]
ax.legend(handles=patches, loc='upper right', fontsize=8)
ax.grid(axis='y', alpha=0.3)
fig.tight_layout()
fig.savefig(f'{OUT}/fraud_z_scores.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"  Saved: {OUT}/fraud_z_scores.png")

# ── Figure 2: Expected vs Actual scatter ─────────────────────────────────────
fig, ax = plt.subplots(figsize=(13, 10))
ax.set_title(
    'Expected vs Actual 2026 Math Score by Province\n'
    '(above diagonal = score higher than trend predicts)',
    fontweight='bold', fontsize=12
)

scatter_df = report_sorted.dropna(subset=['expected_2026', 'actual_2026']).copy()
colors_scatter = scatter_df['fraud_flag'].map({True: '#d62728', False: '#aec7e8'})

ax.scatter(
    scatter_df['expected_2026'],
    scatter_df['actual_2026'],
    c=colors_scatter,
    s=scatter_df['n_2026'].clip(upper=150000) / 600 + 20,
    alpha=0.8,
    edgecolors='gray',
    linewidths=0.5,
    zorder=3,
)

all_vals = pd.concat([scatter_df['expected_2026'], scatter_df['actual_2026']]).dropna()
vmin, vmax = all_vals.min() - 0.1, all_vals.max() + 0.1
diag, = ax.plot([vmin, vmax], [vmin, vmax], 'k--', linewidth=1.2, alpha=0.6, label='Expected = Actual')

for _, row in scatter_df.iterrows():
    pname = PROVINCE_DISPLAY_2026.get(int(row['province']), str(int(row['province'])))
    ax.annotate(
        pname,
        xy=(row['expected_2026'], row['actual_2026']),
        xytext=(4, 4),
        textcoords='offset points',
        fontsize=7 if row['fraud_flag'] else 6,
        color='darkred' if row['fraud_flag'] else 'gray',
        fontweight='bold' if row['fraud_flag'] else 'normal',
    )

# Arrows for 2018 fraud-adjacent
for prov_code in FRAUD_ADJACENT_2026:
    row = scatter_df[scatter_df['province'] == prov_code]
    if len(row) > 0:
        r = row.iloc[0]
        ax.annotate(
            '▲ 2018 adj',
            xy=(r['expected_2026'], r['actual_2026']),
            xytext=(12, -14),
            textcoords='offset points',
            fontsize=7, color='darkred',
            arrowprops=dict(arrowstyle='->', color='darkred', lw=1.0),
        )

ax.set_xlabel('Expected 2026 Math Score  (linear trend from 2021/2022/2024)', fontsize=10)
ax.set_ylabel('Actual 2026 Math Score', fontsize=10)
ax.set_xlim(vmin, vmax)
ax.set_ylim(vmin, vmax)
ax.grid(alpha=0.3, zorder=1)

fraud_patch  = mpatches.Patch(color='#d62728', label='Fraud flagged')
normal_patch = mpatches.Patch(color='#aec7e8', label='Normal')
ax.legend(handles=[fraud_patch, normal_patch, diag], fontsize=9)

fig.tight_layout()
fig.savefig(f'{OUT}/fraud_scatter.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"  Saved: {OUT}/fraud_scatter.png")

print(f"\nDone. Figures saved to {OUT}/")
print("Script complete.")
