"""
Multi-Subject Clustering Cheat Detection — Vietnam THPT 2026
============================================================
Uses DBSCAN on per-student score vectors across multiple subjects,
constrained by SBD proximity, to find groups of students with
near-identical score patterns sitting in the same exam room.

Algorithm
---------
Per province:
  1. Build feature vector per student from K core subjects
  2. Standardize features
  3. Add SBD-index as additional scaled feature (encourages DBSCAN to
     group only spatially-adjacent students)
  4. DBSCAN with tight eps -> groups of near-identical score vectors
  5. Flag clusters of size >= MIN_CLUSTER with small score range & small SBD spread
  6. Compute null expected cluster count under independence

Compares 2026 vs 2024 per province.
"""

import os
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from sklearn.cluster import DBSCAN
warnings.filterwarnings('ignore')

from province_mapping import OLD_TO_NEW_2026, PROVINCE_DISPLAY_2026, FRAUD_ADJACENT_2026

# ─────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────
BASE = '/home/tienda/WorkSpace/HCMUS/PTDLTM/GraduationExamScoreProcessing/Results'
OUT  = '/home/tienda/WorkSpace/HCMUS/PTDLTM/figures'
os.makedirs(OUT, exist_ok=True)

SUBJECTS = ['toan', 'van']
SUBJECTS_2026_SRC = ['toan', 'van', 'ly', 'hoa', 'sinh', 'su', 'dia', 'ngoai ngu']
SUBJECTS_2024_SRC = ['toan', 'ngu_van', 'vat_li', 'hoa_hoc', 'sinh_hoc',
                     'lich_su', 'dia_li', 'ngoai_ngu']
RENAME_2024 = {'ngu_van': 'van', 'vat_li': 'ly', 'hoa_hoc': 'hoa',
               'sinh_hoc': 'sinh', 'lich_su': 'su', 'dia_li': 'dia',
               'ngoai_ngu': 'ngoai_ngu'}

MIN_CLUSTER_SIZE = 3
DBSCAN_EPS       = 0.30      # raw-score space; 0.25 = one grade step
SBD_PROXIMITY_W  = 0.5
MAX_SCORE_RANGE  = 0.25      # near-perfect match required post-hoc
MAX_SBD_SPREAD   = 30        # same exam room (~24-30 seats)
HIGH_MIN_TOAN    = 8.0       # all members must have toan >= this


# ─────────────────────────────────────────────
# Loaders
# ─────────────────────────────────────────────
def load_2026():
    df = pd.read_csv(f'{BASE}/2026/diemthithpt_2026.csv', dtype={'id': str})
    df.columns = df.columns.str.lower().str.strip()
    df = df.rename(columns={'id': 'sbd', 'ngoaingu': 'ngoai_ngu'})
    df = df[['sbd'] + SUBJECTS].copy()
    df['province'] = df['sbd'].str[:2].astype(int)
    for c in SUBJECTS:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df = df.dropna(subset=SUBJECTS)
    df['year'] = 2026
    return df


def load_2024():
    df = pd.read_csv(f'{BASE}/2024/Diemthi2024.csv', dtype={'sbd': str})
    df.columns = df.columns.str.lower().str.strip()
    df['province_old'] = df['sbd'].str[:2].astype(int)
    df['province'] = df['province_old'].map(OLD_TO_NEW_2026)
    df = df[['sbd', 'province'] + SUBJECTS_2024_SRC].rename(columns=RENAME_2024)
    for c in SUBJECTS:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df = df.dropna(subset=SUBJECTS + ['province'])
    df['year'] = 2024
    return df[['sbd', 'province', 'year'] + SUBJECTS]


# ─────────────────────────────────────────────
# Per-province clustering
# ─────────────────────────────────────────────
def cluster_province(df_prov):
    g = df_prov.sort_values('sbd').reset_index(drop=True).reset_index().rename(
        columns={'index': 'sbd_idx'})
    n = len(g)
    if n < MIN_CLUSTER_SIZE:
        return []

    X_scores = g[SUBJECTS].values.astype(float)
    # Raw scores (no standardization) — preserves 0.25 grade granularity
    # so eps=0.30 in raw space ≈ "within one grade step on each subject"
    X_scores_n = X_scores

    sbd_idx = g['sbd_idx'].values.reshape(-1, 1).astype(float)
    # Scale SBD index so adjacent students are within eps distance
    # but students >30 apart exceed eps (encourages room-level grouping)
    sbd_idx_n = sbd_idx / 30.0 * SBD_PROXIMITY_W

    X = np.hstack([X_scores_n, sbd_idx_n])
    db = DBSCAN(eps=DBSCAN_EPS, min_samples=MIN_CLUSTER_SIZE, metric='euclidean').fit(X)
    labels = db.labels_
    unique_labels = sorted(set(labels) - {-1})

    clusters = []
    for lab in unique_labels:
        members = np.where(labels == lab)[0]
        if len(members) < MIN_CLUSTER_SIZE:
            continue
        mg = g.iloc[members]
        sbd_nums = mg['sbd'].astype(str).str.lstrip('0').astype(int).values
        # use last 6 digits for spread
        sbd_int = mg['sbd'].astype(int).values
        sbd_spread = int(sbd_int.max() - sbd_int.min())
        if sbd_spread > MAX_SBD_SPREAD:
            continue

        ranges = {s: float(mg[s].max() - mg[s].min()) for s in SUBJECTS}
        max_range = max(ranges.values())
        if max_range > MAX_SCORE_RANGE:
            continue

        # High-score filter: cluster must be all high achievers (potential collusion)
        mean_toan = float(mg['toan'].mean())
        min_toan  = float(mg['toan'].min())
        if min_toan < HIGH_MIN_TOAN:
            continue

        clusters.append({
            'cluster_size':  len(members),
            'sbd_start':     mg['sbd'].iloc[0],
            'sbd_end':       mg['sbd'].iloc[-1],
            'sbd_spread':    sbd_spread,
            'score_ranges':  ';'.join(f"{s}={ranges[s]:.2f}" for s in SUBJECTS),
            'max_range':     max_range,
            'mean_toan':     mean_toan,
            'min_toan':      min_toan,
            'mean_scores':   ';'.join(f"{s}={mg[s].mean():.2f}" for s in SUBJECTS),
            'scores_toan':   ','.join(f"{v:.2f}" for v in mg['toan'].values),
            'sbd_list':      ','.join(mg['sbd'].tolist()),
        })
    return clusters


def null_expected(df_prov, k=MIN_CLUSTER_SIZE):
    """Expected # clusters under independence across subjects.

    Conditional on toan >= HIGH_MIN_TOAN (matches observed filter).
    For toan: sum P(score in band b)^K over high bands b.
    For van:  sum P(score in band b)^K over all bands b (no high constraint).
    """
    g = df_prov.sort_values('sbd').reset_index(drop=True)
    n = len(g)
    if n < k:
        return 0.0

    p_per_subj_list = []
    for s in SUBJECTS:
        vals = g[s].values
        bands = np.round(vals / 0.25) * 0.25
        bc = pd.Series(bands).value_counts(normalize=True)
        # For toan: restrict to high bands; for others: all bands
        bc_filt = bc[bc.index >= HIGH_MIN_TOAN] if s == 'toan' else bc
        p_subj = 0.0
        for b in bc_filt.index:
            p_w = bc[(bc.index >= b) & (bc.index <= b + 0.25)].sum()
            if p_w > 0:
                p_subj += p_w ** k
        p_per_subj_list.append(p_subj)

    p_joint = float(np.prod(p_per_subj_list))
    return p_joint * n


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────
print("=" * 70)
print("MULTI-SUBJECT DBSCAN CLUSTERING — CHEAT DETECTION")
print(f"subjects={SUBJECTS}")
print(f"min_cluster_size={MIN_CLUSTER_SIZE}  eps={DBSCAN_EPS}  sbd_w={SBD_PROXIMITY_W}")
print("=" * 70)

print("\nLoading 2026...")
df26 = load_2026()
print(f"  2026: {len(df26):,} students, {df26['province'].nunique()} provinces")

print("Loading 2024...")
df24 = load_2024()
print(f"  2024: {len(df24):,} students, {df24['province'].nunique()} provinces")


def run_year(df, year):
    all_clusters, summary = [], []
    for prov, g in df.groupby('province'):
        clu = cluster_province(g)
        expected = null_expected(g)
        observed = len(clu)
        students_in = sum(c['cluster_size'] for c in clu)
        surprise = observed / expected if expected > 0 else (float('inf') if observed > 0 else 0.0)
        summary.append({
            'province':      int(prov),
            'province_name': PROVINCE_DISPLAY_2026.get(int(prov), f'Unknown({prov})'),
            'n_students':    len(g),
            'n_clusters':    observed,
            'students_in_clusters': students_in,
            'expected_clusters': float(expected),
            'surprise_ratio': surprise,
            'max_cluster_size': max((c['cluster_size'] for c in clu), default=0),
        })
        for c in clu:
            c.update({'province': int(prov),
                      'province_name': PROVINCE_DISPLAY_2026.get(int(prov), f'Unknown({prov})'),
                      'year': year})
            all_clusters.append(c)
    return pd.DataFrame(summary), pd.DataFrame(all_clusters)


print("\nClustering 2026 per province...")
sum26, clu26 = run_year(df26, 2026)
print(f"  Flagged {len(clu26)} clusters across {(sum26['n_clusters'] > 0).sum()} provinces")

print("Clustering 2024 per province (baseline)...")
sum24, clu24 = run_year(df24, 2024)
print(f"  Flagged {len(clu24)} clusters across {(sum24['n_clusters'] > 0).sum()} provinces")


# ─────────────────────────────────────────────
# Comparison table
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
cmp['cluster_flag'] = (
    (cmp['surprise_ratio_2026'] >= 100) &
    (cmp['n_clusters_2026'] >= 3)
)
cmp_sorted = cmp.sort_values(
    ['surprise_ratio_2026', 'n_clusters_2026'],
    ascending=[False, False]
).reset_index(drop=True)


# ─────────────────────────────────────────────
# Print
# ─────────────────────────────────────────────
print("\n" + "=" * 70)
print("PER-PROVINCE DBSCAN RESULTS — TOP 25 BY 2026 SURPRISE")
print("=" * 70)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 240)
pd.set_option('display.float_format', '{:.3f}'.format)
top25 = cmp_sorted.head(25)[
    ['province', 'province_name', 'n_students',
     'n_clusters_2026', 'students_in_clusters_2026',
     'expected_clusters_2026', 'surprise_ratio_2026',
     'n_clusters_2024', 'surprise_ratio_2024',
     'cluster_rate_2026', 'fraud_adjacent_2018']
]
print(top25.to_string(index=False))

print(f"\n{'='*70}")
print("NATIONAL TOTALS")
print(f"{'='*70}")
print(f"  2026 clusters: {int(cmp_sorted['n_clusters_2026'].sum()):,}  "
      f"(expected: {cmp_sorted['expected_clusters_2026'].sum():.4f})")
print(f"  2024 clusters: {int(cmp_sorted['n_clusters_2024'].sum()):,}  "
      f"(expected: {cmp_sorted['expected_clusters_2024'].sum():.4f})")
print(f"  2026 students in clusters: {int(cmp_sorted['students_in_clusters_2026'].sum()):,}")
print(f"  2024 students in clusters: {int(cmp_sorted['students_in_clusters_2024'].sum()):,}")

flagged = cmp_sorted[cmp_sorted['cluster_flag']]
print(f"\n{'='*70}")
print(f"CLUSTERING-FRAUD-FLAGGED PROVINCES: {len(flagged)}")
print(f"{'='*70}")
for _, r in flagged.iterrows():
    adj = ' *** 2018 ADJ ***' if r['fraud_adjacent_2018'] else ''
    print(f"\n  [{int(r['province'])}] {r['province_name']}{adj}")
    print(f"     clusters_2026={int(r['n_clusters_2026'])}  expected={r['expected_clusters_2026']:.4f}  "
          f"surprise={r['surprise_ratio_2026']:.1f}x")
    print(f"     students_in_clusters={int(r['students_in_clusters_2026'])}  "
          f"({r['cluster_rate_2026']:.3f}% of province)")
    print(f"     2024 baseline: clusters={int(r['n_clusters_2024'])}, surprise={r['surprise_ratio_2024']:.1f}x")
    print(f"     max_cluster_size={int(r['max_cluster_size'])}")


# ─────────────────────────────────────────────
# Top clusters nationwide
# ─────────────────────────────────────────────
print(f"\n{'='*70}")
print("TOP 15 LARGEST DBSCAN CLUSTERS NATIONWIDE (2026)")
print(f"{'='*70}")
if len(clu26) > 0:
    for _, c in clu26.sort_values('cluster_size', ascending=False).head(15).iterrows():
        print(f"  [{int(c['province'])}] {c['province_name']}  "
              f"size={c['cluster_size']}  "
              f"sbd={c['sbd_start']}-{c['sbd_end']}  spread={c['sbd_spread']}  "
              f"max_range={c['max_range']:.2f}")
        print(f"     means: {c['mean_scores']}")
        print(f"     toan:  [{c['scores_toan']}]")


# ─────────────────────────────────────────────
# Save
# ─────────────────────────────────────────────
cmp_sorted.to_csv(f'{OUT}/clustering_results.csv', index=False)
print(f"\nSaved per-province: {OUT}/clustering_results.csv")
if len(clu26) > 0:
    clu26.to_csv(f'{OUT}/clustering_2026_detail.csv', index=False)
    print(f"Saved 2026 detail: {OUT}/clustering_2026_detail.csv")
if len(clu24) > 0:
    clu24.to_csv(f'{OUT}/clustering_2024_detail.csv', index=False)
    print(f"Saved 2024 detail: {OUT}/clustering_2024_detail.csv")


# ─────────────────────────────────────────────
# Figures
# ─────────────────────────────────────────────
print("\nGenerating figures...")

fig, ax = plt.subplots(figsize=(20, 8))
ax.set_title(
    'Multi-Subject DBSCAN Cluster Signal (per province) - 2026\n'
    'Observed / Expected ratio of near-identical score-vector clusters within SBD-neighborhood',
    fontweight='bold', fontsize=12
)
plot_df = cmp_sorted[cmp_sorted['surprise_ratio_2026'] > 0].sort_values(
    'surprise_ratio_2026', ascending=False).reset_index(drop=True)
labels = [f"{PROVINCE_DISPLAY_2026.get(int(p), str(int(p)))}\n[{int(p)}]"
          for p in plot_df['province']]
colors = []
for _, r in plot_df.iterrows():
    if r['cluster_flag']:
        colors.append('#d62728')
    elif r['surprise_ratio_2026'] > 100:
        colors.append('#ff7f0e')
    elif r['surprise_ratio_2026'] > 10:
        colors.append('#ffd700')
    else:
        colors.append('#aec7e8')

ax.bar(range(len(plot_df)), plot_df['surprise_ratio_2026'],
       color=colors, alpha=0.85, edgecolor='white')
ax.axhline(100, color='red',    linestyle='--', linewidth=1.0, label='100x')
ax.axhline(10,  color='orange', linestyle='--', linewidth=1.0, label='10x')
ax.axhline(1,   color='gray',   linestyle='-',  linewidth=0.8, alpha=0.5, label='Expected (1x)')

for i, r in plot_df.iterrows():
    if r['fraud_adjacent_2018']:
        ax.annotate('2018',
                    xy=(i, r['surprise_ratio_2026']),
                    xytext=(i, r['surprise_ratio_2026'] * 1.15 + 1),
                    fontsize=7, color='darkred', ha='center', fontweight='bold')

ax.set_xticks(range(len(plot_df)))
ax.set_xticklabels(labels, fontsize=6.5, rotation=45, ha='right')
ax.set_ylabel('Surprise Ratio (observed / expected)', fontsize=10)
ax.set_yscale('log')
patches = [
    mpatches.Patch(color='#d62728', label='Cluster fraud flagged'),
    mpatches.Patch(color='#ff7f0e', label='>100x surprise'),
    mpatches.Patch(color='#ffd700', label='10-100x surprise'),
    mpatches.Patch(color='#aec7e8', label='<=10x surprise'),
]
ax.legend(handles=patches, loc='upper right', fontsize=8)
ax.grid(axis='y', alpha=0.3)
fig.tight_layout()
fig.savefig(f'{OUT}/clustering_surprise.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"  Saved: {OUT}/clustering_surprise.png")

# Cluster size distribution
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle('DBSCAN Cluster Size Distribution - Multi-Subject Score Vectors',
             fontweight='bold', fontsize=12)
for ax, (df_c, yr, color) in zip(axes,
        [(clu26, 2026, '#d62728'), (clu24, 2024, '#1f77b4')]):
    if len(df_c) > 0:
        sizes = df_c['cluster_size'].value_counts().sort_index()
        ax.bar(sizes.index, sizes.values, color=color, alpha=0.75, edgecolor='white')
        for x, y in zip(sizes.index, sizes.values):
            ax.text(x, y, str(y), ha='center', va='bottom', fontsize=9)
        ax.set_title(f'{yr}: {len(df_c)} clusters, max size={df_c["cluster_size"].max()}',
                     fontsize=10)
    else:
        ax.set_title(f'{yr}: no clusters flagged', fontsize=10)
    ax.set_xlabel('Cluster size (students)', fontsize=9)
    ax.set_ylabel('Count', fontsize=9)
    ax.grid(axis='y', alpha=0.3)
fig.tight_layout()
fig.savefig(f'{OUT}/clustering_size_dist.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"  Saved: {OUT}/clustering_size_dist.png")

print("\nScript complete.")
