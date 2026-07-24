"""
Student-Level Cluster Cheat Detection — Vietnam THPT 2026
=========================================================
Detects suspicious clusters of consecutive SBD (student IDs) with
near-identical high scores. Consecutive SBD ≈ same exam room (24-30 seats).

Hypothesis: under independent scoring, P(K consecutive students all score
in narrow high band) is astronomically small. Clusters signal collusion.

Detection (per province)
------------------------
1. Sort students by SBD within each province
2. Slide K-window over present students
3. Flag window if:
   - All K scores >= HIGH_THRESH (e.g., 8.0)
   - Range within window <= RANGE_THRESH (e.g., 0.25 = one grade step)
4. Merge overlapping flagged windows -> cluster
5. Compute expected count under independence -> surprise ratio

Compares 2026 vs 2024 baseline per province.
"""

import os
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from numpy.lib.stride_tricks import sliding_window_view
warnings.filterwarnings('ignore')

from config import BASE, OUT

from province_mapping import OLD_TO_NEW_2026, PROVINCE_DISPLAY_2026, FRAUD_ADJACENT_2026

# ─────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────

SUBJECT      = 'toan'
K_WINDOW     = 5            # consecutive present students
HIGH_THRESH  = 8.0          # all scores must be >= this
RANGE_THRESH = 0.25         # max - min within window (0.25 = one grade step)


# ─────────────────────────────────────────────
# Loaders
# ─────────────────────────────────────────────
def load_2026():
    df = pd.read_csv(f'{BASE}/2026/diemthithpt_2026.csv', dtype={'id': str})
    df.columns = df.columns.str.lower().str.strip()
    df = df[['id', SUBJECT]].rename(columns={'id': 'sbd', SUBJECT: 'score'})
    df['province'] = df['sbd'].str[:2].astype(int)
    df['score'] = pd.to_numeric(df['score'], errors='coerce')
    df['year'] = 2026
    return df.dropna(subset=['score'])


def load_2024():
    df = pd.read_csv(f'{BASE}/2024/Diemthi2024.csv', dtype={'sbd': str})
    df.columns = df.columns.str.lower().str.strip()
    df = df[['sbd', SUBJECT]].rename(columns={SUBJECT: 'score'}).copy()
    df['province_old'] = df['sbd'].str[:2].astype(int)
    df['province'] = df['province_old'].map(OLD_TO_NEW_2026)
    df['score'] = pd.to_numeric(df['score'], errors='coerce')
    df['year'] = 2024
    return df.dropna(subset=['score', 'province'])


# ─────────────────────────────────────────────
# Cluster detector — single province
# ─────────────────────────────────────────────
def detect_clusters(df_prov):
    """Sort by SBD, slide K-window, flag all-high & near-identical windows."""
    g = df_prov.sort_values('sbd').reset_index(drop=True)
    scores = g['score'].values
    sbds   = g['sbd'].values
    n      = len(scores)
    if n < K_WINDOW:
        return []

    win        = sliding_window_view(scores, K_WINDOW)
    win_min    = win.min(axis=1)
    win_max    = win.max(axis=1)
    win_range  = win_max - win_min
    win_all_hi = (win >= HIGH_THRESH).all(axis=1)
    win_flag   = win_all_hi & (win_range <= RANGE_THRESH)

    if not win_flag.any():
        return []

    flag_idx = np.where(win_flag)[0]
    clusters = []
    cur_s, cur_e = flag_idx[0], flag_idx[0] + K_WINDOW - 1
    for idx in flag_idx[1:]:
        ws, we = idx, idx + K_WINDOW - 1
        if ws <= cur_e:
            cur_e = max(cur_e, we)
        else:
            clusters.append((cur_s, cur_e))
            cur_s, cur_e = ws, we
    clusters.append((cur_s, cur_e))

    out = []
    for cs, ce in clusters:
        bs = scores[cs:ce + 1]
        out.append({
            'cluster_size':  len(bs),
            'sbd_start':     sbds[cs],
            'sbd_end':       sbds[ce],
            'score_min':     float(bs.min()),
            'score_max':     float(bs.max()),
            'score_range':   float(bs.max() - bs.min()),
            'score_mean':    float(bs.mean()),
            'scores':        ','.join(f'{s:.2f}' for s in bs),
        })
    return out


def null_expected(df_prov, k=K_WINDOW):
    """E[# flagged windows] under independence.

    For each high band b in [HIGH_THRESH, 10], compute p_window = P(score in
    [b, b+RANGE_THRESH]) empirically, then P(K students all in that band) =
    p_window^K. Sum across all possible high bands and multiply by #windows.
    """
    g = df_prov.sort_values('sbd').reset_index(drop=True)
    scores = g['score'].values
    n = len(scores)
    if n < k:
        return 0.0, 0

    bands = np.round(scores / 0.25) * 0.25
    bc    = pd.Series(bands).value_counts(normalize=True)
    n_bands_in_range = max(1, int(round(RANGE_THRESH / 0.25)))

    p_all = 0.0
    high_bands = bc.index[bc.index >= HIGH_THRESH]
    for b in high_bands:
        # sum probability over a windowed band of width RANGE_THRESH starting at b
        p_w = bc[(bc.index >= b) & (bc.index <= b + RANGE_THRESH)].sum()
        if p_w > 0:
            p_all += p_w ** k

    return p_all * (n - k + 1), n - k + 1


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────
print("=" * 70)
print("STUDENT-LEVEL CLUSTER CHEAT DETECTION — VIETNAM THPT")
print(f"Subject={SUBJECT}  K_window={K_WINDOW}  High>={HIGH_THRESH}  Range<={RANGE_THRESH}")
print("=" * 70)

print("\nLoading 2026...")
df26 = load_2026()
print(f"  2026: {len(df26):,} students across {df26['province'].nunique()} provinces")

print("Loading 2024...")
df24 = load_2024()
print(f"  2024: {len(df24):,} students across {df24['province'].nunique()} provinces")


def run_year(df, year):
    all_clusters, summary_rows = [], []
    for prov, g in df.groupby('province'):
        clusters = detect_clusters(g)
        expected, n_win = null_expected(g)
        observed = len(clusters)
        students_in_clusters = sum(c['cluster_size'] for c in clusters)
        surprise = observed / expected if expected > 0 else (float('inf') if observed > 0 else 0.0)
        summary_rows.append({
            'province':      int(prov),
            'province_name': PROVINCE_DISPLAY_2026.get(int(prov), f'Unknown({prov})'),
            'n_students':    len(g),
            'n_windows':     n_win,
            'n_clusters':    observed,
            'students_in_clusters': students_in_clusters,
            'expected_clusters': float(expected),
            'surprise_ratio': surprise,
            'max_cluster_size': max((c['cluster_size'] for c in clusters), default=0),
        })
        for c in clusters:
            c['province']      = int(prov)
            c['province_name'] = PROVINCE_DISPLAY_2026.get(int(prov), f'Unknown({prov})')
            c['year']          = year
            all_clusters.append(c)
    return pd.DataFrame(summary_rows), pd.DataFrame(all_clusters)


print("\nDetecting 2026 clusters (per province)...")
sum26, clu26 = run_year(df26, 2026)
print(f"  Flagged {len(clu26)} clusters across {(sum26['n_clusters'] > 0).sum()} provinces")

print("Detecting 2024 clusters (per province, baseline)...")
sum24, clu24 = run_year(df24, 2024)
print(f"  Flagged {len(clu24)} clusters across {(sum24['n_clusters'] > 0).sum()} provinces")


# ─────────────────────────────────────────────
# Per-province comparison table
# ─────────────────────────────────────────────
cmp = sum26.merge(
    sum24[['province', 'n_clusters', 'students_in_clusters',
           'expected_clusters', 'surprise_ratio']],
    on='province', how='left', suffixes=('_2026', '_2024')
).fillna(0)

cmp['delta_clusters']    = cmp['n_clusters_2026'] - cmp['n_clusters_2024']
cmp['cluster_rate_2026'] = cmp['students_in_clusters_2026'] / cmp['n_students'] * 100
cmp['cluster_rate_2024'] = cmp['students_in_clusters_2024'] / cmp['n_students'] * 100
cmp['fraud_adjacent_2018'] = cmp['province'].isin(FRAUD_ADJACENT_2026)

cmp_sorted = cmp.sort_values(
    ['surprise_ratio_2026', 'n_clusters_2026'],
    ascending=[False, False]
).reset_index(drop=True)

cmp_sorted['cluster_flag'] = (
    (cmp_sorted['surprise_ratio_2026'] > 50) &
    (cmp_sorted['n_clusters_2026'] >= 5) &
    (cmp_sorted['n_clusters_2026'] > cmp_sorted['n_clusters_2024'] * 1.5)
)


# ─────────────────────────────────────────────
# Print per-province results
# ─────────────────────────────────────────────
print("\n" + "=" * 70)
print("PER-PROVINCE CLUSTER ANALYSIS — TOP 25 BY 2026 SURPRISE")
print("=" * 70)

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 240)
pd.set_option('display.float_format', '{:.3f}'.format)

top25 = cmp_sorted.head(25)[
    ['province', 'province_name', 'n_students',
     'n_clusters_2026', 'students_in_clusters_2026',
     'expected_clusters_2026', 'surprise_ratio_2026',
     'n_clusters_2024', 'surprise_ratio_2024',
     'cluster_rate_2026', 'cluster_rate_2024',
     'fraud_adjacent_2018']
]
print(top25.to_string(index=False))

print(f"\n{'='*70}")
print("NATIONAL TOTALS")
print(f"{'='*70}")
print(f"  2026 clusters:        {int(cmp_sorted['n_clusters_2026'].sum()):,}  "
      f"(expected under independence: {cmp_sorted['expected_clusters_2026'].sum():.2f})")
print(f"  2024 clusters:        {int(cmp_sorted['n_clusters_2024'].sum()):,}  "
      f"(expected under independence: {cmp_sorted['expected_clusters_2024'].sum():.2f})")
print(f"  2026 students in clusters: {int(cmp_sorted['students_in_clusters_2026'].sum()):,}")
print(f"  2024 students in clusters: {int(cmp_sorted['students_in_clusters_2024'].sum()):,}")
print(f"  Delta clusters 2026-2024:  {int(cmp_sorted['n_clusters_2026'].sum() - cmp_sorted['n_clusters_2024'].sum()):+,}")

flagged = cmp_sorted[cmp_sorted['cluster_flag']]
print(f"\n{'='*70}")
print(f"CLUSTER-FRAUD-FLAGGED PROVINCES: {len(flagged)}")
print(f"{'='*70}")
for _, row in flagged.iterrows():
    adj = ' *** 2018 ADJ ***' if row['fraud_adjacent_2018'] else ''
    print(f"\n  [{int(row['province'])}] {row['province_name']}{adj}")
    print(f"     clusters_2026={int(row['n_clusters_2026'])}  expected={row['expected_clusters_2026']:.3f}  "
          f"surprise={row['surprise_ratio_2026']:.1f}x")
    print(f"     students_in_clusters={int(row['students_in_clusters_2026'])}  "
          f"({row['cluster_rate_2026']:.3f}% of province)")
    print(f"     2024 baseline: {int(row['n_clusters_2024'])} clusters, surprise={row['surprise_ratio_2024']:.1f}x")
    print(f"     max_cluster_size={int(row['max_cluster_size'])}")


# ─────────────────────────────────────────────
# Largest suspicious clusters nationwide
# ─────────────────────────────────────────────
print(f"\n{'='*70}")
print("TOP 15 LARGEST SUSPICIOUS CLUSTERS NATIONWIDE (2026)")
print(f"{'='*70}")
if len(clu26) > 0:
    clu26_sorted = clu26.sort_values('cluster_size', ascending=False).head(15)
    for _, c in clu26_sorted.iterrows():
        print(f"  [{int(c['province'])}] {c['province_name']}  "
              f"size={c['cluster_size']}  "
              f"sbd={c['sbd_start']}-{c['sbd_end']}  "
              f"range={c['score_min']:.2f}-{c['score_max']:.2f}  "
              f"scores=[{c['scores']}]")


# ─────────────────────────────────────────────
# Save
# ─────────────────────────────────────────────
out_csv = f'{OUT}/cluster_detection_results.csv'
cmp_sorted.to_csv(out_csv, index=False)
print(f"\nSaved per-province summary: {out_csv}")

if len(clu26) > 0:
    clu_out = f'{OUT}/cluster_detection_2026_detail.csv'
    clu26.to_csv(clu_out, index=False)
    print(f"Saved 2026 cluster detail: {clu_out}")

if len(clu24) > 0:
    clu_out24 = f'{OUT}/cluster_detection_2024_detail.csv'
    clu24.to_csv(clu_out24, index=False)
    print(f"Saved 2024 cluster detail: {clu_out24}")


# ─────────────────────────────────────────────
# Figures
# ─────────────────────────────────────────────
print("\nGenerating figures...")

# Figure 1: Surprise ratio by province (log scale)
fig, ax = plt.subplots(figsize=(20, 8))
ax.set_title(
    f'Student-Level Cluster Cheat Signal (per province) - 2026 {SUBJECT.upper()}\n'
    f'Observed / Expected ratio of K={K_WINDOW} consecutive SBD clusters '
    f'(score >= {HIGH_THRESH}, range <= {RANGE_THRESH})',
    fontweight='bold', fontsize=12
)
plot_df = cmp_sorted[cmp_sorted['surprise_ratio_2026'] > 0].copy()
plot_df = plot_df.sort_values('surprise_ratio_2026', ascending=False).reset_index(drop=True)
labels = [f"{PROVINCE_DISPLAY_2026.get(int(p), str(int(p)))}\n[{int(p)}]"
          for p in plot_df['province']]

colors = []
for _, r in plot_df.iterrows():
    if r['cluster_flag']:
        colors.append('#d62728')
    elif r['surprise_ratio_2026'] > 50:
        colors.append('#ff7f0e')
    elif r['surprise_ratio_2026'] > 10:
        colors.append('#ffd700')
    else:
        colors.append('#aec7e8')

ax.bar(range(len(plot_df)), plot_df['surprise_ratio_2026'],
       color=colors, alpha=0.85, edgecolor='white')
ax.axhline(50, color='red',    linestyle='--', linewidth=1.0, label='50x surprise')
ax.axhline(10, color='orange', linestyle='--', linewidth=1.0, label='10x surprise')
ax.axhline(1,  color='gray',   linestyle='-',  linewidth=0.8, alpha=0.5, label='Expected (1x)')

for i, row in plot_df.iterrows():
    if row['fraud_adjacent_2018']:
        ax.annotate('2018',
                    xy=(i, row['surprise_ratio_2026']),
                    xytext=(i, row['surprise_ratio_2026'] * 1.15 + 1),
                    fontsize=7, color='darkred', ha='center', fontweight='bold')

ax.set_xticks(range(len(plot_df)))
ax.set_xticklabels(labels, fontsize=6.5, rotation=45, ha='right')
ax.set_ylabel('Surprise Ratio (observed / expected clusters)', fontsize=10)
ax.set_yscale('log')
ax.set_xlabel('Province', fontsize=10)
patches = [
    mpatches.Patch(color='#d62728', label='Cluster fraud flagged'),
    mpatches.Patch(color='#ff7f0e', label='>50x surprise'),
    mpatches.Patch(color='#ffd700', label='10-50x surprise'),
    mpatches.Patch(color='#aec7e8', label='<=10x surprise'),
]
ax.legend(handles=patches, loc='upper right', fontsize=8)
ax.grid(axis='y', alpha=0.3)
fig.tight_layout()
fig.savefig(f'{OUT}/cluster_surprise_ratio.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"  Saved: {OUT}/cluster_surprise_ratio.png")

# Figure 2: 2026 vs 2024 cluster rate per province
fig, ax = plt.subplots(figsize=(11, 10))
ax.set_title(
    f'Per-Province Cluster Rate: 2026 vs 2024\n'
    f'% students in flagged K={K_WINDOW} clusters',
    fontweight='bold', fontsize=12
)
scatter_df = cmp_sorted.dropna(subset=['cluster_rate_2026', 'cluster_rate_2024']).copy()
max_val = max(scatter_df['cluster_rate_2026'].max(),
              scatter_df['cluster_rate_2024'].max()) + 0.05
ax.plot([0, max_val], [0, max_val], 'k--', linewidth=1.0, alpha=0.6, label='2026 = 2024')
ax.plot([0, max_val], [0, max_val * 2], 'r--', linewidth=0.8, alpha=0.5, label='2x inflation')

colors_scatter = scatter_df['cluster_flag'].map({True: '#d62728', False: '#aec7e8'})
ax.scatter(scatter_df['cluster_rate_2024'], scatter_df['cluster_rate_2026'],
           c=colors_scatter, s=60, alpha=0.75, edgecolors='gray', linewidths=0.5)
for _, row in scatter_df.iterrows():
    if row['cluster_flag'] or row['fraud_adjacent_2018']:
        pname = PROVINCE_DISPLAY_2026.get(int(row['province']), str(int(row['province'])))
        ax.annotate(pname,
                    xy=(row['cluster_rate_2024'], row['cluster_rate_2026']),
                    xytext=(3, 3), textcoords='offset points',
                    fontsize=8, color='darkred', fontweight='bold')

ax.set_xlabel('2024 cluster rate (%)', fontsize=10)
ax.set_ylabel('2026 cluster rate (%)', fontsize=10)
ax.set_xlim(-0.01, max_val)
ax.set_ylim(-0.01, max_val)
ax.grid(alpha=0.3)
fraud_patch = mpatches.Patch(color='#d62728', label='Cluster fraud flagged')
norm_patch  = mpatches.Patch(color='#aec7e8', label='Normal')
ax.legend(handles=[fraud_patch, norm_patch], loc='upper left', fontsize=9)
fig.tight_layout()
fig.savefig(f'{OUT}/cluster_2026_vs_2024.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"  Saved: {OUT}/cluster_2026_vs_2024.png")

print("\nScript complete.")
