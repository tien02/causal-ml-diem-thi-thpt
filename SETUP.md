# Setup & Dataset Preparation Guide

Causal Inference Analysis — Vietnam National High School Exam Scores (2021–2026)

---

## 1. Prerequisites

### System Requirements
- Python 3.9+
- ~3GB disk space (raw CSV + outputs)
- Enough RAM for large dataframes (~8GB recommended)

### Install Dependencies

```bash
pip install -q pandas numpy matplotlib seaborn scipy scikit-learn
pip install -q statsmodels networkx
pip install -q econml dowhy
```

Verify installation:
```bash
python -c "import pandas, numpy, econml, dowhy; print('✓ All packages OK')"
```

---

## 2. Dataset Preparation

### 2.1 Data Structure

Expected directory layout:
```
PTDLTM/
├── GraduationExamScoreProcessing/
│   └── Results/
│       ├── Diemthi2021.csv          (5.38M rows total, ~650K rows 2021)
│       ├── Diemthi2022.csv          (~850K rows)
│       ├── 2024/
│       │   └── Diemthi2024.csv      (~860K rows)
│       ├── 2025/
│       │   ├── 20250715-ketquathi-ct2018a.csv  (CT2018 curriculum, ~840K)
│       │   └── 20250715-ketquathi-ct2006.csv   (CT2006 curriculum, legacy)
│       └── 2026/
│           └── diemthithpt_2026.csv (CT2025 reform, ~1.2M rows)
```

### 2.2 Data Files & Formats

| Year | File | Format | Size | Subject Schema | Notes |
|------|------|--------|------|---|---|
| **2021** | `Diemthi2021.csv` | CSV | ~650K | `toan`, `nguvan`, `vatly`, `hoahoc`, `sinhhoc`, `lichsu`, `dialy` | SBD format: `PPCCC` (2-digit province code) |
| **2022** | `Diemthi2022.csv` | CSV | ~850K | same | SBD format: `PPCCC` |
| **2024** | `2024/Diemthi2024.csv` | CSV | ~860K | same | SBD format: `PPCCC` |
| **2025** | `2025/20250715-ketquathi-ct2018a.csv` | CSV (`;` sep) | ~840K | same | **Semicolon delimiter**, UTF-8 encoded. CT2018 curriculum. Both curricula 2025→2026 transition |
| **2026** | `2026/diemthithpt_2026.csv` | CSV | ~1.2M | `toan`, `van`, `ly`, `hoa`, `sinh`, `su`, `dia`, `ktpl`, `tin`, `congnghiep`, `nongnghiep`, `ngoaingu`, `mangoaingu` | Column renames: `van`→`nguvan`, `ly`→`vatly`, `hoa`→`hoahoc`, etc. CT2025 curriculum begins. |

### 2.3 Download Data (if missing)

Data files are from the **[tien02/GraduationExamScoreProcessing](https://github.com/tien02/GraduationExamScoreProcessing)** repository.

**Option A: Clone & Sync (if you have access)**
```bash
cd GraduationExamScoreProcessing
git pull origin main
```

**Option B: Manual Download from External Source**

If data files are hosted externally (e.g., MinIO, S3, Google Drive), download and place them in the correct `Results/` directory structure shown above.

**Verify CSV files exist:**
```bash
cd /home/tienda/WorkSpace/HCMUS/PTDLTM/GraduationExamScoreProcessing/Results
ls -lh Diemthi2021.csv Diemthi2022.csv 2024/Diemthi2024.csv 2025/20250715-ketquathi-ct2018a.csv 2026/diemthithpt_2026.csv
```

### 2.4 Extract Compressed Files (if needed)

Some archives may need extraction:
```bash
cd GraduationExamScoreProcessing/Results

# Extract 2024 if Diemthi2024.zip exists
unzip -o Diemthi2024.zip

# Extract 2025 if zip exists
unzip -o Diemthi2025.zip

# Extract 2026 if zip exists
unzip -o Diemthi2026.zip
```

### 2.5 Validate Data

Quick sanity checks:
```python
import pandas as pd

# Check 2021
df21 = pd.read_csv('GraduationExamScoreProcessing/Results/Diemthi2021.csv', 
                    dtype={'SBD': str, 'Cum_thi': str})
print(f"2021: {len(df21)} rows, columns: {df21.columns.tolist()}")

# Check 2026
df26 = pd.read_csv('GraduationExamScoreProcessing/Results/2026/diemthithpt_2026.csv', 
                    dtype={'id': str})
print(f"2026: {len(df26)} rows, columns: {df26.columns.tolist()}")

# Check province extraction
df26['province'] = df26['id'].str[:2].apply(lambda x: int(x) if x.isdigit() else None)
print(f"2026 Province coverage: {df26['province'].nunique()} unique provinces")
```

---

## 3. Running the Analysis

All Python scripts assume working directory = `/home/tienda/WorkSpace/HCMUS/PTDLTM/`.

### 3.1 Full Pipeline (Sequential)

Run all analyses in recommended order:

```bash
cd /home/tienda/WorkSpace/HCMUS/PTDLTM

# 1. Descriptive stats, DiD, province mapping
python analysis.py

# 2. Anomaly detection (2026 fraud flags)
python fraud_detection.py

# 3. RDD + Double ML + HTE
python causal_ml.py

# 4. Synthetic Control + EconML + sensitivity analysis
python synthetic_control.py

# 5. DoWhy DAG + refutation tests
python dowhy_refutation.py
```

**Total runtime:** ~10–20 minutes (depends on data size & compute)

### 3.2 Individual Scripts

Run any script standalone:

```bash
# Descriptive analysis only
python analysis.py

# Fraud detection only
python fraud_detection.py

# Causal ML (RDD, Double ML)
python causal_ml.py

# Synthetic Control
python synthetic_control.py

# DoWhy refutation
python dowhy_refutation.py

# Detect clustering fraud (DBSCAN multi-subject)
python clustering_detection.py
```

### 3.3 Script Descriptions & Outputs

| Script | Purpose | Output | Chapters |
|--------|---------|--------|----------|
| **analysis.py** | DiD (COVID impact), OLS regressions, KDE plots, Province merger crosswalk, Urban/Rural gaps | `figures/*.png` | 2, 3, 4, 5, 6, 7 |
| **fraud_detection.py** | Z-score & KL divergence anomaly detection 2026 | `figures/fraud_*.png` | 8 |
| **causal_ml.py** | RDD (within-2025 cutoff), Double ML (5-fold), HTE by urban tier | `figures/causal_*.png`, `figures/hte_*.png` | 9 |
| **synthetic_control.py** | SCM (33 provinces, pre: 2021/22/24), LinearDML, CausalForestDML, Rosenbaum Bounds, Monte Carlo sensitivity | `figures/sc_*.png`, `figures/sensitivity_*.png` | 10 |
| **dowhy_refutation.py** | Causal DAG (GML), backdoor identification, placebo/RCC/subset refutation tests | `figures/dag_*.png` | 11 |
| **cluster_cheat_detection.py** | K-Window sliding (consecutive SBD) + high scores | `figures/cluster_*.png` | 12 |
| **clustering_detection.py** | DBSCAN multi-subject (spatial + score alignment) | Cluster labels | 12 |
| **province_mapping.py** | Utility: 63→34 province crosswalk, urban tier lookup, etc. | *Module* | — |

### 3.4 Outputs

- **Figures:** All plots saved to `figures/` directory (~35+ PNG files, ~200MB total)
- **Console logs:** Analysis status + key statistics printed to stdout
- **Report:** Markdown chapters in `report/_chapters/` (populated by scripts or manual)

Check progress:
```bash
ls -lh figures/ | tail -20
wc -l figures/*
```

---

## 4. Troubleshooting

### Error: `FileNotFoundError: .../Diemthi2021.csv`

**Cause:** CSV files not in expected directory.

**Fix:**
```bash
# Verify directory structure
find GraduationExamScoreProcessing/Results -name "*.csv" -type f

# Ensure paths match script expectations
# Scripts expect: /home/tienda/WorkSpace/HCMUS/PTDLTM/GraduationExamScoreProcessing/Results/
```

### Error: `UnicodeDecodeError` on 2025 file

**Cause:** Encoding mismatch (2025 file is UTF-8-sig with `;` delimiters).

**Fix:** Already handled in `load_2025()`:
```python
df = pd.read_csv(..., sep=';', encoding='utf-8-sig')
```

### Error: `ImportError: No module named 'econml'`

**Cause:** Missing dependency.

**Fix:**
```bash
pip install econml
```

### Error: `OutOfMemoryError`

**Cause:** System running low on RAM when loading large DataFrames.

**Workaround:** Process one year at a time, or increase swap space.

### Slow performance

**Cause:** HDD bottleneck or large dataset size.

**Optimization:**
- Use SSD if possible
- Reduce sample size in scripts (change random seed or `df.sample(frac=0.5)`)
- Run scripts with `nice -n 10 python analysis.py`

---

## 5. Data Schema & Standardization

### Subject Name Mapping

Scripts standardize column names across years:

| Old Name (2021/22/24) | New Name (standardized) | Units |
|---|---|---|
| `ngu_van` | `nguvan` | 0.0–10.0 |
| `ngoai_ngu` | `ngoaingu` | 0.0–10.0 |
| `vat_li` / `vat_ly` | `vatly` | 0.0–10.0 |
| `hoa_hoc` | `hoahoc` | 0.0–10.0 |
| `sinh_hoc` | `sinhhoc` | 0.0–10.0 |
| `lich_su` | `lichsu` | 0.0–10.0 |
| `dia_li` / `dia_ly` | `dialy` | 0.0–10.0 |
| `ktpl` | `gdcd` (added 2022+) | 0.0–10.0 |
| — | `toan` | 0.0–10.0 (unchanged) |

### Key Variables

| Variable | Source | Values | Notes |
|----------|--------|--------|-------|
| `province` | Extract from SBD (first 2 digits) | 01–63 (old), 01–34 (2026 merged) | See `province_mapping.py` for crosswalk |
| `year` | Added by loader | 2021, 2022, 2024, 2025, 2026 | — |
| `sbd` | Original student ID | String | Key for tracking anomalies |
| Subject scores | CSV direct | 0.0–10.0 (float) | Missing = NaN |

---

## 6. Reproducibility & Variations

### Configuration

Key parameters in scripts (editable):

- **`analysis.py`:**
  - `COMMON_SUBJECTS` — subjects to include in descriptive stats
  - `CUTOFF_2025` — RDD cutoff year (default: 2025)
  - Province mappings from `province_mapping.py`

- **`fraud_detection.py`:**
  - `Z_THRESHOLD` — anomaly threshold (default: 2.0 σ)
  - `KL_THRESHOLD` — divergence cutoff (default: 0.5)

- **`synthetic_control.py`:**
  - Pre-treatment periods: `2021, 2022, 2024`
  - Treatment period: `2025` (CT2018 starts)
  - `GAMMA_RANGE` — Rosenbaum sensitivity (default: 1.0 to 6.0)

- **`monte_carlo_2025_2026.py`:**
  - `N_MONTE_CARLO` — iterations (default: 10,000)
  - `ADAPTATION_RATE` — learning curve slope

### Randomness

Set seed for reproducibility:
```python
import numpy as np
import random

seed = 42
np.random.seed(seed)
random.seed(seed)
```

---

## 7. Performance Benchmarks

On standard laptop (8GB RAM, SSD):

| Script | Runtime | Output Size |
|--------|---------|------------|
| `analysis.py` | 2–3 min | 50MB (figures + logs) |
| `fraud_detection.py` | 30 sec | 10MB |
| `causal_ml.py` | 5–7 min | 80MB (HTE + plots) |
| `synthetic_control.py` | 8–10 min | 100MB (SCM + sensitivity) |
| `dowhy_refutation.py` | 3–4 min | 20MB |
| **Total** | **~20 min** | **~260MB** |

---

## 8. CI/CD Integration (Optional)

Run all scripts + validate outputs:
```bash
#!/bin/bash
set -e

cd /home/tienda/WorkSpace/HCMUS/PTDLTM

echo "[1/5] Running analysis.py..."
python analysis.py

echo "[2/5] Running fraud_detection.py..."
python fraud_detection.py

echo "[3/5] Running causal_ml.py..."
python causal_ml.py

echo "[4/5] Running synthetic_control.py..."
python synthetic_control.py

echo "[5/5] Running dowhy_refutation.py..."
python dowhy_refutation.py

echo "✓ All scripts complete. Outputs in figures/"
ls -lh figures/ | head -20
```

Save as `run_all.sh` and execute:
```bash
chmod +x run_all.sh
./run_all.sh
```

---

## References

- **Data source:** [tien02/GraduationExamScoreProcessing](https://github.com/tien02/GraduationExamScoreProcessing)
- **Province mapping:** `province_mapping.py` (63→34 crosswalk)
- **Full report:** `report/_chapters/FULL_REPORT.md`
