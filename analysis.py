"""
Causal Analysis: Vietnam University Entrance Exam Scores
Years available: 2021, 2022, 2024, 2025, 2026
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from scipy import stats
import statsmodels.formula.api as smf
import statsmodels.api as sm
import warnings
warnings.filterwarnings('ignore')

from province_mapping import (
    PROVINCE_NAMES_OLD as PROVINCE_NAMES,
    CHUYEN_STRONG_OLD as CHUYEN_STRONG,
    CHUYEN_STRONG_2026,
    FEE_EXEMPT_OLD as FEE_EXEMPT,
    FEE_EXEMPT_2026,
    FRAUD_2018_OLD,
    OLD_TO_NEW_2026,
    PROVINCE_DISPLAY_2026,
    urban_tier_old, urban_tier_2026,
    get_name_old, get_name_2026,
)
from config import BASE, OUT
from gdp_province import add_grdp_column

# ─────────────────────────────────────────────
# Data loading
# ─────────────────────────────────────────────

def load_2021():
    df = pd.read_csv(f'{BASE}/Diemthi2021.csv', dtype={'SBD': str, 'Cum_thi': str})
    df.columns = df.columns.str.lower().str.strip()
    df['province'] = df['cum_thi'].str.zfill(2).str[:2].apply(
        lambda x: int(x) if x.isdigit() else np.nan)
    df['year'] = 2021
    df.rename(columns={'ngu_van':'nguvan','ngoai_ngu':'ngoaingu',
                        'vat_ly':'vatly','hoa_hoc':'hoahoc',
                        'sinh_hoc':'sinhhoc','lich_su':'lichsu','dia_ly':'dialy'}, inplace=True)
    return df

def load_2022():
    df = pd.read_csv(f'{BASE}/Diemthi2022.csv', dtype={'sbd': str})
    df.columns = df.columns.str.lower().str.strip()
    df['province'] = df['sbd'].str[:2].apply(lambda x: int(x) if x.isdigit() else np.nan)
    df['year'] = 2022
    df.rename(columns={'ngu_van':'nguvan','ngoai_ngu':'ngoaingu',
                        'vat_li':'vatly','hoa_hoc':'hoahoc',
                        'sinh_hoc':'sinhhoc','lich_su':'lichsu','dia_li':'dialy'}, inplace=True)
    return df

def load_2024():
    df = pd.read_csv(f'{BASE}/2024/Diemthi2024.csv', dtype={'sbd': str})
    df.columns = df.columns.str.lower().str.strip()
    df['province'] = df['sbd'].str[:2].apply(lambda x: int(x) if x.isdigit() else np.nan)
    df['year'] = 2024
    df.rename(columns={'ngu_van':'nguvan','ngoai_ngu':'ngoaingu',
                        'vat_li':'vatly','hoa_hoc':'hoahoc',
                        'sinh_hoc':'sinhhoc','lich_su':'lichsu','dia_li':'dialy'}, inplace=True)
    return df

def load_2025():
    df = pd.read_csv(f'{BASE}/2025/20250715-ketquathi-ct2018a.csv',
                     sep=';', dtype={'sbd': str}, encoding='utf-8-sig')
    df.columns = df.columns.str.lower().str.strip()
    df['province'] = df['sbd'].str[:2].apply(lambda x: int(x) if x.isdigit() else np.nan)
    df['year'] = 2025
    df.rename(columns={'ngu_van':'nguvan','ngoai_ngu':'ngoaingu',
                        'vat_li':'vatly','hoa_hoc':'hoahoc',
                        'sinh_hoc':'sinhhoc','lich_su':'lichsu','dia_li':'dialy'}, inplace=True)
    return df

def load_2026():
    df = pd.read_csv(f'{BASE}/2026/diemthithpt_2026.csv', dtype={'id': str})
    df.columns = df.columns.str.lower().str.strip()
    df.rename(columns={'id':'sbd','van':'nguvan','ly':'vatly',
                        'hoa':'hoahoc','sinh':'sinhhoc','su':'lichsu',
                        'dia':'dialy','ktpl':'gdcd'}, inplace=True)
    df['province'] = df['sbd'].str[:2].apply(lambda x: int(x) if x.isdigit() else np.nan)
    df['year'] = 2026
    return df

print("Loading data...")
dfs = {}
for year, loader in [(2021, load_2021), (2022, load_2022),
                     (2024, load_2024), (2025, load_2025), (2026, load_2026)]:
    print(f"  {year}...", end='', flush=True)
    dfs[year] = loader()
    print(f" {len(dfs[year]):,} rows")

COMMON_SUBJECTS = ['toan','nguvan','ngoaingu','vatly','hoahoc','sinhhoc','lichsu','dialy','gdcd']

for year, df in dfs.items():
    for col in COMMON_SUBJECTS:
        if col not in df.columns:
            df[col] = np.nan
        else:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    if year == 2026:
        df['urban_tier']         = df['province'].apply(lambda p: urban_tier_2026(int(p)) if pd.notna(p) else 'Unknown')
        df['is_chuyen_province'] = df['province'].apply(lambda p: int(p) in CHUYEN_STRONG_2026 if pd.notna(p) else False)
        df['province_harmonized'] = df['province'].astype('Int64')
    else:
        df['urban_tier']         = df['province'].apply(lambda p: urban_tier_old(int(p)) if pd.notna(p) else 'Unknown')
        df['is_chuyen_province'] = df['province'].apply(lambda p: int(p) in CHUYEN_STRONG if pd.notna(p) else False)
        df['province_harmonized'] = df['province'].map(OLD_TO_NEW_2026)
    add_grdp_column(df, year)
    df['khoi_A'] = df[['toan','vatly','hoahoc']].sum(axis=1, min_count=3)
    df['khoi_C'] = df[['nguvan','lichsu','dialy']].sum(axis=1, min_count=3)
    df['khoi_D'] = df[['toan','nguvan','ngoaingu']].sum(axis=1, min_count=3)
    df['toan_9plus'] = df['toan'] >= 9.0

ALL = pd.concat(dfs.values(), ignore_index=True)
print(f"\nTotal: {len(ALL):,} rows, years: {sorted(ALL['year'].unique())}")

# ─────────────────────────────────────────────
# PART 1: COVID EXOGENOUS SHOCK
# ─────────────────────────────────────────────
print("\n=== PART 1: COVID IMPACT ===")

covid_years = [2021, 2022, 2024, 2025, 2026]
subjects_covid = ['toan', 'nguvan', 'ngoaingu']
covid_stats = []
for year in covid_years:
    df = dfs[year]
    for subj in subjects_covid:
        valid = df[subj].dropna()
        if len(valid) < 1000: continue
        covid_stats.append({
            'year': year, 'subject': subj,
            'mean': valid.mean(), 'median': valid.median(),
            'std': valid.std(), 'n': len(valid),
            'pct_below5': (valid < 5).mean() * 100,
            'pct_above8': (valid >= 8).mean() * 100,
        })
covid_df = pd.DataFrame(covid_stats)
print(covid_df.to_string(index=False))

# DiD: Urban vs Rural recovery 2021→2024
print("\n--- DiD: COVID effect by urban tier ---")
did_data = ALL[ALL['year'].isin([2021, 2024])][['year','urban_tier','toan']].dropna()
did_pivot = did_data.groupby(['year','urban_tier'])['toan'].mean().unstack()
print(did_pivot)
if 'Đô thị lớn' in did_pivot.columns and 'Tỉnh lẻ/Nông thôn' in did_pivot.columns:
    did_urban = did_pivot.loc[2024,'Đô thị lớn']   - did_pivot.loc[2021,'Đô thị lớn']
    did_rural = did_pivot.loc[2024,'Tỉnh lẻ/Nông thôn'] - did_pivot.loc[2021,'Tỉnh lẻ/Nông thôn']
    print(f"\nDiD (Toán, Urban vs Rural, 2021→2024): {did_urban - did_rural:.4f}")
    print(f"  Urban recovery: {did_urban:+.4f}")
    print(f"  Rural recovery: {did_rural:+.4f}")

u21 = dfs[2021]['toan'].dropna()
u24 = dfs[2024]['toan'].dropna()
stat, p = stats.mannwhitneyu(
    u21.sample(min(50000, len(u21)), random_state=42),
    u24.sample(min(50000, len(u24)), random_state=42),
    alternative='two-sided')
print(f"\nMann-Whitney Toán 2021 vs 2024: p={p:.4e}, mean_21={u21.mean():.3f}, mean_24={u24.mean():.3f}")

# ─────────────────────────────────────────────
# PART 2: URBAN vs RURAL
# ─────────────────────────────────────────────
print("\n=== PART 2: URBAN vs RURAL ===")

urban_stats = ALL[ALL['year'].isin([2024, 2026])].groupby('urban_tier').agg(
    n=('toan','count'),
    toan_mean=('toan','mean'),
    toan_std=('toan','std'),
    nguvan_mean=('nguvan','mean'),
    ngoaingu_mean=('ngoaingu','mean'),
    khoi_A_mean=('khoi_A','mean'),
    toan_9plus_pct=('toan_9plus','mean'),
).round(3)
print(urban_stats)

ols_data = dfs[2024][['toan','urban_tier']].dropna()
ols_data['urban_large'] = (ols_data['urban_tier'] == 'Đô thị lớn').astype(int)
ols_data['urban_mid']   = (ols_data['urban_tier'] == 'Đô thị vừa').astype(int)
model = smf.ols('toan ~ urban_large + urban_mid', data=ols_data).fit()
print(f"\nOLS Toán ~ urban_large + urban_mid (2024):")
print(f"  urban_large coef: {model.params['urban_large']:.4f} (p={model.pvalues['urban_large']:.4e})")
print(f"  urban_mid coef:   {model.params['urban_mid']:.4f}   (p={model.pvalues['urban_mid']:.4e})")
print(f"  R²: {model.rsquared:.4f}")

prov_rank = dfs[2024].groupby('province').agg(
    n=('toan','count'), toan_mean=('toan','mean'), toan_9plus=('toan_9plus','mean'),
).query('n > 500').sort_values('toan_mean', ascending=False)
prov_rank['name'] = prov_rank.index.map(PROVINCE_NAMES)
print("\nTop 15 provinces by mean Math (2024):")
print(prov_rank[['name','n','toan_mean','toan_9plus']].head(15).to_string())
print("\nBottom 10 provinces by mean Math (2024):")
print(prov_rank[['name','n','toan_mean','toan_9plus']].tail(10).to_string())

# ─────────────────────────────────────────────
# PART 3: CHUYEN SCHOOL PROXY EFFECT
# ─────────────────────────────────────────────
print("\n=== PART 3: CHUYEN SCHOOL EFFECT ===")

for year in [2022, 2024]:
    df = dfs[year].dropna(subset=['toan'])
    total_9plus   = (df['toan'] >= 9).sum()
    chuyen_9plus  = df[df['is_chuyen_province'] & (df['toan'] >= 9)].shape[0]
    chuyen_total  = df[df['is_chuyen_province']].shape[0]
    total         = len(df)
    if total > 0 and total_9plus > 0 and chuyen_total > 0:
        concentration = (chuyen_9plus / total_9plus) / (chuyen_total / total)
        print(f"{year}: Chuyên provinces {concentration:.2f}x concentration of 9+ scorers")
        print(f"       Pop share: {chuyen_total/total*100:.1f}%, Top-scorer share: {chuyen_9plus/total_9plus*100:.1f}%")

for year in [2024]:
    df = dfs[year]
    chuyen = df[df['is_chuyen_province']]['toan'].dropna()
    others = df[~df['is_chuyen_province']]['toan'].dropna()
    stat, p = stats.mannwhitneyu(
        chuyen.sample(min(50000, len(chuyen)), random_state=42),
        others.sample(min(50000, len(others)), random_state=42),
        alternative='greater')
    print(f"\n{year} Chuyên-strong: mean={chuyen.mean():.3f}  Others: mean={others.mean():.3f}  p={p:.4e}")

prov_chuyen = dfs[2024].groupby('province').agg(
    n=('toan','count'), pct_9plus=('toan_9plus','mean'),
).query('n > 1000')
prov_chuyen['name']     = prov_chuyen.index.map(PROVINCE_NAMES)
prov_chuyen['is_chuyen'] = prov_chuyen.index.isin(CHUYEN_STRONG)
print("\nTop 15 provinces by % Math ≥ 9 (2024):")
print(prov_chuyen.sort_values('pct_9plus', ascending=False)[
    ['name','n','pct_9plus','is_chuyen']].head(15).to_string())

# ─────────────────────────────────────────────
# PART 4: LOCAL POLICY / FEE EXEMPTION
# ─────────────────────────────────────────────
print("\n=== PART 4: LOCAL POLICY / FEE EXEMPTION ===")

for year in [2022, 2024]:
    df = dfs[year].dropna(subset=['province','toan']).copy()
    df['fee_exempt'] = df['province'].isin(FEE_EXEMPT)
    exempt     = df[df['fee_exempt']]['toan']
    non_exempt = df[~df['fee_exempt']]['toan']
    print(f"\n{year} Fee-exempt mean: {exempt.mean():.3f} (n={len(exempt):,}), std={exempt.std():.3f}")
    print(f"{year} Non-exempt mean:  {non_exempt.mean():.3f} (n={len(non_exempt):,}), std={non_exempt.std():.3f}")
    print(f"  % < 5  exempt={( exempt<5).mean()*100:.1f}%  non-exempt={(non_exempt<5).mean()*100:.1f}%")
    print(f"  % >= 8 exempt={(exempt>=8).mean()*100:.1f}%  non-exempt={(non_exempt>=8).mean()*100:.1f}%")

print("\n--- Gap HN+HCM vs National mean (Toán) ---")
for year, df in sorted(dfs.items()):
    d = df.dropna(subset=['province','toan'])
    national = d['toan'].mean()
    hn_hcm_codes = {1, 79} if year == 2026 else {1, 2}
    hn_hcm = d[d['province'].isin(hn_hcm_codes)]['toan'].mean()
    if not np.isnan(hn_hcm):
        print(f"  {year}: National={national:.3f}, HN+HCM={hn_hcm:.3f}, Gap={hn_hcm-national:+.3f}")

# ─────────────────────────────────────────────
# FIGURES
# ─────────────────────────────────────────────
print("\nGenerating figures...")

COLORS = ['#e63946','#457b9d','#2a9d8f','#e9c46a','#f4a261']
plt.rcParams.update({'font.size': 12})

# FIG 1: Mean scores by year (bar chart with errorbars)
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.suptitle('Fig 1: COVID Shock — Score Distributions by Year', fontweight='bold', fontsize=14)
for ax, subj, title in zip(axes,
    ['toan','nguvan','ngoaingu'],
    ['Toan (Math)','Ngu van (Literature)','Ngoai ngu (Foreign Lang)']):
    valid_years = [y for y in covid_years if subj in dfs[y] and len(dfs[y][subj].dropna()) > 1000]
    means = [dfs[y][subj].dropna().mean() for y in valid_years]
    stds  = [dfs[y][subj].dropna().std()  for y in valid_years]
    ax.bar(range(len(valid_years)), means, color=COLORS[:len(valid_years)],
           yerr=stds, capsize=4, alpha=0.85)
    ax.set_xticks(range(len(valid_years)))
    ax.set_xticklabels(valid_years)
    ax.set_ylabel('Diem trung binh')
    ax.set_title(title)
    ax.set_ylim(0, 10)
    ax.axhline(5.0, color='gray', linestyle='--', alpha=0.5)
    ax.axvspan(-0.5, 0.5, alpha=0.08, color='red')
    for i, (m, s) in enumerate(zip(means, stds)):
        ax.text(i, m + s + 0.15, f'{m:.2f}', ha='center', fontsize=9)
fig.tight_layout()
fig.savefig(f'{OUT}/fig1_covid_mean_scores.png', dpi=150, bbox_inches='tight')
plt.close()

# FIG 2: KDE distributions Math 2021 vs 2022 vs 2024
fig, ax = plt.subplots(figsize=(10, 5))
ax.set_title('Fig 2: COVID — Phan phoi diem Toan (2021 vs 2022 vs 2024)', fontweight='bold')
for year, color, label in [(2021,'#e63946','2021 (COVID)'),
                            (2022,'#f4a261','2022 (Hau COVID)'),
                            (2024,'#2a9d8f','2024 (Binh thuong)')]:
    s = dfs[year]['toan'].dropna().sample(50000, random_state=42)
    s.plot.kde(ax=ax, color=color, label=label, linewidth=2)
ax.set_xlabel('Diem Toan')
ax.set_ylabel('Mat do xac suat')
ax.legend()
ax.set_xlim(0, 10)
ax.axvline(5.0, color='gray', linestyle='--', alpha=0.5)
fig.tight_layout()
fig.savefig(f'{OUT}/fig2_covid_kde_toan.png', dpi=150, bbox_inches='tight')
plt.close()

# FIG 3: DiD — Urban vs Rural recovery
fig, ax = plt.subplots(figsize=(9, 5))
ax.set_title('Fig 3: DiD — Phuc hoi diem sau COVID (Toan: 2021 vs 2024)', fontweight='bold')
did_series = ALL[ALL['year'].isin([2021, 2024])].groupby(['year','urban_tier'])['toan'].mean().reset_index()
for tier, color in [('Do thi lon','#e63946'),('Do thi vua','#457b9d'),('Tinh le/Nong thon','#2a9d8f')]:
    sub = did_series[did_series['urban_tier'].str.contains(tier.split()[0], na=False)]
    if sub.empty:
        sub = did_series[did_series['urban_tier'] == tier]
    if sub.empty:
        sub = did_series[did_series['urban_tier'].apply(lambda x: tier.split('/')[0] in x or x.startswith(tier[:4]))]
for tier_key, tier_label, color in [
    ('Đô thị lớn','Do thi lon','#e63946'),
    ('Đô thị vừa','Do thi vua','#457b9d'),
    ('Tỉnh lẻ/Nông thôn','Tinh le/Nong thon','#2a9d8f')]:
    sub = did_series[did_series['urban_tier'] == tier_key]
    if not sub.empty:
        ax.plot(sub['year'], sub['toan'], marker='o', color=color, label=tier_label, linewidth=2.5, markersize=8)
        for _, row in sub.iterrows():
            ax.annotate(f"{row['toan']:.3f}", (row['year'], row['toan']),
                        textcoords='offset points', xytext=(0, 8), ha='center', fontsize=9)
ax.set_xlabel('Nam')
ax.set_ylabel('Diem Toan trung binh')
ax.legend()
ax.set_xticks([2021, 2024])
ax.set_xlim(2020.5, 2024.5)
ax.grid(axis='y', alpha=0.3)
fig.tight_layout()
fig.savefig(f'{OUT}/fig3_did_covid_urban_rural.png', dpi=150, bbox_inches='tight')
plt.close()

# FIG 4: Urban vs Rural KDE (2024)
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.suptitle('Fig 4: Khoang cach Do thi / Nong thon (2024)', fontweight='bold')
tier_colors = {'Đô thị lớn':'#e63946','Đô thị vừa':'#457b9d','Tỉnh lẻ/Nông thôn':'#2a9d8f'}
tier_labels = {'Đô thị lớn':'Do thi lon','Đô thị vừa':'Do thi vua','Tỉnh lẻ/Nông thôn':'Tinh le'}
for ax, subj, title in zip(axes, ['toan','nguvan','ngoaingu'], ['Toan','Ngu van','Ngoai ngu']):
    for tier, color in tier_colors.items():
        s = dfs[2024][dfs[2024]['urban_tier'] == tier][subj].dropna()
        if len(s) > 100:
            s.sample(min(30000, len(s)), random_state=42).plot.kde(
                ax=ax, color=color, label=f'{tier_labels[tier]} (mu={s.mean():.2f})', linewidth=2)
    ax.set_title(title); ax.set_xlabel('Diem'); ax.set_xlim(0, 10); ax.legend(fontsize=8)
fig.tight_layout()
fig.savefig(f'{OUT}/fig4_urban_rural_2024.png', dpi=150, bbox_inches='tight')
plt.close()

# FIG 5: Province ranking Math 2024 (top 30)
fig, ax = plt.subplots(figsize=(14, 9))
ax.set_title('Fig 5: Diem Toan trung binh theo Tinh (2024) — Top 30', fontweight='bold')
top30 = prov_rank.head(30).copy()
bar_colors = ['#e63946' if i in CHUYEN_STRONG else '#457b9d' for i in top30.index]
ax.barh(range(len(top30)), top30['toan_mean'], color=bar_colors, alpha=0.85)
ax.set_yticks(range(len(top30)))
ax.set_yticklabels(top30['name'], fontsize=9)
ax.set_xlabel('Diem Toan trung binh')
ax.axvline(prov_rank['toan_mean'].mean(), color='gray', linestyle='--')
red_p  = mpatches.Patch(color='#e63946', label='Tinh chuyen manh')
blue_p = mpatches.Patch(color='#457b9d', label='Tinh khac')
ax.legend(handles=[red_p, blue_p])
for i, (_, row) in enumerate(top30.iterrows()):
    ax.text(row['toan_mean'] + 0.01, i, f"{row['toan_mean']:.3f}", va='center', fontsize=8)
ax.invert_yaxis()
fig.tight_layout()
fig.savefig(f'{OUT}/fig5_province_ranking_2024.png', dpi=150, bbox_inches='tight')
plt.close()

# FIG 6: Top-scorer rate by province (chuyên proxy)
fig, ax = plt.subplots(figsize=(14, 8))
ax.set_title('Fig 6: Ti le % thi sinh dat 9+ Toan theo Tinh (2024) — proxy chuyen', fontweight='bold')
top_pct = prov_chuyen.sort_values('pct_9plus', ascending=False).head(30)
bar_colors6 = ['#e63946' if i in CHUYEN_STRONG else '#457b9d' for i in top_pct.index]
ax.barh(range(len(top_pct)), top_pct['pct_9plus'] * 100, color=bar_colors6, alpha=0.85)
ax.set_yticks(range(len(top_pct)))
ax.set_yticklabels(top_pct['name'], fontsize=9)
ax.set_xlabel('% thi sinh dat >= 9 diem Toan')
red_p  = mpatches.Patch(color='#e63946', label='Tinh chuyen manh')
blue_p = mpatches.Patch(color='#457b9d', label='Tinh khac')
ax.legend(handles=[red_p, blue_p])
for i, (_, row) in enumerate(top_pct.iterrows()):
    ax.text(row['pct_9plus'] * 100 + 0.05, i, f"{row['pct_9plus']*100:.2f}%", va='center', fontsize=8)
ax.invert_yaxis()
fig.tight_layout()
fig.savefig(f'{OUT}/fig6_chuyen_top_scorer_rate.png', dpi=150, bbox_inches='tight')
plt.close()

# FIG 7: Chuyên strong vs others KDE (2024)
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.suptitle('Fig 7: Phan phoi diem — Tinh chuyen manh vs Tinh khac (2024)', fontweight='bold')
for ax, subj, title in zip(axes, ['toan','nguvan','ngoaingu'], ['Toan','Ngu van','Ngoai ngu']):
    for label, flag, color in [('Chuyen manh', True,'#e63946'),('Tinh khac', False,'#457b9d')]:
        s = dfs[2024][dfs[2024]['is_chuyen_province'] == flag][subj].dropna()
        if len(s) > 100:
            s.sample(min(30000, len(s)), random_state=42).plot.kde(
                ax=ax, color=color, label=f'{label} (mu={s.mean():.2f})', linewidth=2)
    ax.set_title(title); ax.set_xlabel('Diem'); ax.set_xlim(0, 10); ax.legend(fontsize=9)
fig.tight_layout()
fig.savefig(f'{OUT}/fig7_chuyen_score_dist.png', dpi=150, bbox_inches='tight')
plt.close()

# FIG 8: Fee exemption effect (2024)
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
fig.suptitle('Fig 8: Tac dong Chinh sach Mien phi thi — Phan phoi diem (2024)', fontweight='bold')
df24 = dfs[2024].copy()
df24['fee_exempt'] = df24['province'].isin(FEE_EXEMPT)
for ax, subj, title in zip(axes, ['toan','ngoaingu'], ['Toan','Ngoai ngu']):
    for label, flag, color in [('Mien phi thi', True,'#e63946'),('Dong phi', False,'#457b9d')]:
        s = df24[df24['fee_exempt'] == flag][subj].dropna()
        if len(s) > 100:
            s.sample(min(50000, len(s)), random_state=42).plot.kde(
                ax=ax, color=color, label=f'{label} (mu={s.mean():.2f}, sd={s.std():.2f})', linewidth=2)
    ax.set_title(title); ax.set_xlabel('Diem'); ax.set_xlim(0, 10); ax.legend()
fig.tight_layout()
fig.savefig(f'{OUT}/fig8_fee_exemption_effect.png', dpi=150, bbox_inches='tight')
plt.close()

# FIG 9: HN+HCM gap trend over years
years_trend = sorted(dfs.keys())
national_means, hn_hcm_means, gaps = [], [], []
for year in years_trend:
    d = dfs[year].dropna(subset=['province','toan'])
    national_means.append(d['toan'].mean())
    hn_hcm_means.append(d[d['province'].isin({1,2})]['toan'].mean())
    gaps.append(hn_hcm_means[-1] - national_means[-1])

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
fig.suptitle('Fig 9: Xu huong — Khoang cach HN+HCM vs Ca nuoc (Toan)', fontweight='bold')
ax1.plot(years_trend, national_means, 'o-', color='#457b9d', label='Ca nuoc', linewidth=2)
ax1.plot(years_trend, hn_hcm_means,  's-', color='#e63946', label='Ha Noi + TP.HCM', linewidth=2)
ax1.set_ylabel('Diem Toan trung binh'); ax1.set_xlabel('Nam'); ax1.legend(); ax1.grid(alpha=0.3)
for y, n, h in zip(years_trend, national_means, hn_hcm_means):
    ax1.annotate(f'{n:.2f}', (y, n), textcoords='offset points', xytext=(-18, 5),  fontsize=8, color='#457b9d')
    ax1.annotate(f'{h:.2f}', (y, h), textcoords='offset points', xytext=(-18, -12), fontsize=8, color='#e63946')
ax2.bar(years_trend, gaps, color=['#e63946' if g > 0 else '#457b9d' for g in gaps], alpha=0.8)
ax2.set_ylabel('Khoang cach (HN+HCM - Ca nuoc)'); ax2.set_xlabel('Nam')
ax2.axhline(0, color='gray', linestyle='--')
ax2.set_title('Gap HN+HCM vs Trung binh quoc gia')
for y, g in zip(years_trend, gaps):
    ax2.text(y, g + 0.005 * np.sign(g), f'{g:+.3f}', ha='center', fontsize=9)
fig.tight_layout()
fig.savefig(f'{OUT}/fig9_hn_hcm_gap_trend.png', dpi=150, bbox_inches='tight')
plt.close()

# FIG 10: Heatmap province x year (harmonized to 2026 admin codes)
print("Building heatmap...")
valid_years_heat = [y for y in [2021, 2022, 2024, 2026] if y in dfs]
heat_data = {year: dfs[year].groupby('province_harmonized')['toan'].mean() for year in valid_years_heat}
heat_df = pd.DataFrame(heat_data).dropna(subset=valid_years_heat, thresh=2)
heat_df['name'] = heat_df.index.map(lambda i: get_name_2026(int(i)) if pd.notna(i) else 'Unknown')
heat_df['avg']  = heat_df[valid_years_heat].mean(axis=1)
heat_top = heat_df.sort_values('avg', ascending=False).head(25)
fig, ax = plt.subplots(figsize=(10, 10))
ax.set_title('Fig 10: Diem Toan TB theo Tinh x Nam (Top 25)', fontweight='bold')
hm = heat_top[valid_years_heat].values
im = ax.imshow(hm, aspect='auto', cmap='RdYlGn', vmin=4, vmax=8)
ax.set_xticks(range(len(valid_years_heat))); ax.set_xticklabels(valid_years_heat)
ax.set_yticks(range(len(heat_top))); ax.set_yticklabels(heat_top['name'], fontsize=9)
for i in range(len(heat_top)):
    for j in range(len(valid_years_heat)):
        v = hm[i, j]
        if not np.isnan(v):
            ax.text(j, i, f'{v:.2f}', ha='center', va='center', fontsize=8,
                    color='black' if 4.5 < v < 7.5 else 'white')
plt.colorbar(im, ax=ax, label='Diem Toan TB')
fig.tight_layout()
fig.savefig(f'{OUT}/fig10_heatmap_province_year.png', dpi=150, bbox_inches='tight')
plt.close()

# ─────────────────────────────────────────────
# SUMMARY TABLE
# ─────────────────────────────────────────────
print("\n=== NATIONAL MEANS BY YEAR ===")
rows = []
for year, df in sorted(dfs.items()):
    row = {'year': year, 'n': len(df)}
    for s in ['toan','nguvan','ngoaingu','vatly','hoahoc','sinhhoc','lichsu','dialy','gdcd']:
        col = df[s].dropna()
        row[f'{s}'] = round(col.mean(), 3) if len(col) > 0 else np.nan
    rows.append(row)
print(pd.DataFrame(rows).to_string(index=False))

print(f"\nDone. Figures saved to {OUT}/")
print("Files:", sorted(os.listdir(OUT)))
