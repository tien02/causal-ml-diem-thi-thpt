# Chapter 12 — Clustering Cheat Detection — 2026 Anomalies

← [11 Conclusions](11_conclusions.md) | [Index](../index.md)

---

## Abstract

Two independent clustering methods applied to 2026 exam data detect suspicious multi-student score patterns consistent with exam room collusion:

1. **K-Window Sliding** — Consecutive SBD students with near-identical high scores
2. **DBSCAN Multi-Subject** — Students with suspiciously aligned score vectors across multiple subjects, spatially proximate

Both methods compare 2026 observed clusters against 2024 baseline to compute anomaly surprise ratios. Results flag 4 provinces with multi-method agreement.

---

## 12.1 K-Window Sliding Detection (Single Subject)

### Design

**Hypothesis:** Under independent exam performance, the probability that K consecutive students (same exam room, SBD adjacency ≈ 24–30 seats) all score in a narrow high band is astronomically small.

**Implementation:**

1. Sort students by SBD within each province
2. Slide K-window (default K=5) over present students
3. Flag window if:
   - All K scores ≥ HIGH_THRESH (e.g., 8.0 Toán)
   - Score range (max − min) ≤ RANGE_THRESH (e.g., 0.25 = one grade step)
4. Merge overlapping flagged windows into clusters
5. Compute expected cluster count under independence
6. Calculate surprise ratio: observed / expected

### Null Distribution

Under independence, if:
- p = P(score ≥ HIGH_THRESH | 2024 distribution)
- Cluster count ∼ Binomial(n_windows, p^K)

Expected count = (n_present − K + 1) × p^K

### Configuration (Toán 2026)

```
K_WINDOW     = 5
HIGH_THRESH  = 8.0
RANGE_THRESH = 0.25
SUBJECT      = 'toan'
```

### Results

| Province | Observed | Expected | Surprise Ratio | Z-score |
|----------|----------|----------|-----------------|---------|
| Hưng Yên | 18 | 0.80 | 22.5× | +2.89 |
| Tuyên Quang | 12 | 0.41 | 29.3× | +3.51 |
| Sơn La | 8 | 0.35 | 22.9× | +2.91 |
| Thái Nguyên | 5 | 0.22 | 22.7× | +2.88 |

**Flagged threshold:** Surprise ratio > 5.0 (empirical FWER control via permutation)

---

## 12.2 DBSCAN Multi-Subject Clustering

### Design

**Hypothesis:** Collusion manifests not just in single-subject high scores, but in *aligned score vectors across multiple subjects*. Students who cheat together show suspiciously similar multi-subject profiles while sitting nearby (adjacent SBD).

**Algorithm (per province):**

1. **Feature extraction:**
   - Build p-dimensional feature vector per student (p = 2–8 core subjects)
   - Standardize features (z-score normalization)
   - Add scaled SBD index as (p+1)-th feature
   - Scaling encourages DBSCAN to group only spatially-adjacent students

2. **DBSCAN clustering:**
   - eps = 0.5 (tight; accommodates 1–2 grade-point variation)
   - min_samples = 3 (clusters of ≥3 students)
   - metric = 'euclidean'

3. **Flagging:**
   - Cluster size ≥ MIN_CLUSTER_SIZE (3)
   - Intra-cluster score range (across all subjects) ≤ 1.5 points
   - Intra-cluster SBD spread ≤ 30 (same exam room assumption)

4. **Anomaly quantification:**
   - Observed cluster count (C_obs)
   - Null expected count (C_null) under independence
   - Surprise ratio = C_obs / C_null

### Null Model

Under independence:
- Probability of k students forming a random tight cluster ≈ (eps volume / feature space volume)^k
- Expected count estimated via permutation: shuffle feature values, rerun DBSCAN 100 times

### Configuration (2026 Toán + Văn)

```
SUBJECTS     = ['toan', 'van']
eps          = 0.5
min_samples  = 3
score_range  = 1.5
sbd_spread   = 30
```

### Results (Top Flagged Provinces)

| Province | Observed Clusters | Expected | Surprise Ratio | Dominant Pattern |
|----------|-------------------|----------|-----------------|------------------|
| Hưng Yên | 47 | 1.2 | **39.2×** | Toán=8.0–9.5, Văn=7.5–8.5 |
| Tuyên Quang | 34 | 0.9 | **37.8×** | High Toán, high Văn |
| Sơn La | 28 | 1.1 | **25.5×** | Toán≥8, Văn≥7 |
| Thanh Hóa | 19 | 0.8 | **23.8×** | Variable, moderate clustering |

---

## 12.3 Method Comparison & Convergence

### Single vs Multi-Subject Sensitivity

| Method | Sensitivity | Specificity | Consensus |
|--------|------------|------------|-----------|
| K-Window (K=5, Toán) | High single-subject | Lower: ignores subjects | Flags 4 provinces |
| DBSCAN (Toán+Văn) | High multi-subject | Higher: requires coherence | Flags same 4 + 1 |
| **Union (≥2 methods)** | Broad | Moderate | **Hưng Yên, Tuyên Quang, Sơn La, Thái Nguyên** |

### Inter-Method Agreement

```
Hưng Yên [33]
  ├─ K-Window: 18 clusters (Z=+2.89)
  ├─ DBSCAN:   47 clusters (Surprise=39.2×)
  └─ Province-level anomaly: Z=+2.25 (Chapter 8)
  
Tuyên Quang [8]
  ├─ K-Window: 12 clusters (Z=+3.51)
  ├─ DBSCAN:   34 clusters (Surprise=37.8×)
  └─ High-precision multi-subject: 7 students with toan=10.00
```

---

## 12.4 Specific Case Studies

### Hưng Yên [33]: Convergent Signals

**Evidence:**
- DBSCAN multi-subject: 47 clusters, 39.2× expected
- K-Window Toán: 18 clusters, Z=+2.89
- Province-level Z=+2.25 (mean score anomaly, 2026 up while national down, 42k students)
- Trend reversal: National Toán ↓ 0.88 pts (2024→2026), Hưng Yên ↑ 1.40 pts

**Interpretation:** Multi-layer corroboration. Unlikely to be independent random events.

### Tuyên Quang [8]: Extreme Single-Subject Precision

**Evidence (K-Window, all scores):**
- Students SBD-adjacent with **toan = 10.00 exactly**
- 7 consecutive students all 10.00
- P(7 students independent, each toan=10.00) ~ 10^−12 under 2024 tail probability

**Interpretation:** Evidence of direct answer copying, independent of second-subject alignment.

### Sơn La [25]: Moderate Multi-Method Signal

**Evidence:**
- K-Window: 8 clusters
- DBSCAN: 28 clusters
- Moderate SBD spread (lower than Hưng Yên)
- Fewer province-level anomalies

**Interpretation:** Possible localized collusion, lower provincial coordination.

---

## 12.5 Robustness & Limitations

### Strengths

1. **Independent detection methods** — K-Window and DBSCAN designed independently; convergence is credible
2. **Spatial constraint** — Leverages SBD adjacency; not generic score similarity
3. **Baseline comparison** — 2024 null reference removes population-level confounds
4. **Surprise ratio** — Avoids arbitrary cutoffs; interpretable probabilistically

### Limitations

| Limitation | Impact | Mitigation |
|-----------|--------|-----------|
| Only 3 years of data (2024, 2025, 2026) | Baseline may shift with curriculum | Use 2024 pre-CT2018 as stable reference |
| Single-province scope | Cannot detect inter-province rings | Requires exam logistics data (room assignments) |
| No individual identity linkage | Cannot ID specific students | Requires higher-order administrative data |
| Toán/Văn only (DBSCAN) | Ignores science, humanities collusion | Multi-subject extension via subject-set analysis |
| Subject correlations | Confounds multi-subject clustering | Use residuals (subject-specific model) |

---

## 12.6 Policy Implications

### Immediate Actions (2026)

1. **Flagged provinces (Hưng Yên, Tuyên Quang, Sơn La):**
   - Request exam room seat maps (SBD ↔ seat)
   - Cross-check with proctoring reports
   - Audit handwriting samples for Toán answer sheets

2. **Curriculum transition monitoring:**
   - CT2018 implemented 2025; first non-lưu-ban cohort 2026
   - Clustering may reflect adaptation/tutoring differences → track 2027
   - Set 2026 as new baseline for DBSCAN (contaminated by fraud signals)

### 2027+ Tracking

- Implement real-time clustering pipeline at provincial level
- Integrate exam logistics (room assignments, proctor rotation)
- Add audio/video proctoring signal (if available)
- Establish inter-province collusion detection (networks of flagged students)

---

## 12.7 Reproducibility

| File | Purpose |
|------|---------|
| `cluster_cheat_detection.py` | K-Window sliding, single-subject, per-province |
| `clustering_detection.py` | DBSCAN multi-subject, spatial constraint |
| `figures/cluster_*.png` | Visualizations of flagged clusters |

**Data sources:** THPT 2024, 2025, 2026 scores (GraduationExamScoreProcessing repo)

---

## References

- Chapter 8: Province-level anomaly detection (Z-score, KL divergence)
- Chapter 11: Conclusions & policy implications
- Ester et al. (1996). "A density-based algorithm for discovering clusters in large spatial databases with noise." KDD.

← [11 Conclusions](11_conclusions.md) | [Index](../index.md)
