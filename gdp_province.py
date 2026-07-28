"""
GRDP per capita by province for Vietnam university entrance exam analysis.

Source: General Statistics Office of Vietnam (GSO) via Wikipedia
  https://vi.wikipedia.org/wiki/Danh_sach_don_vi_hanh_chinh_Viet_Nam_theo_GRDP_binh_quan_dau_nguoi

Data: 2022 GRDP per capita at current prices (million VND/person/year).
Used as socioeconomic control variable for 2021-2025 exam cohorts.

For 2026 merged provinces: simple average of constituent old-province values
(population-weighted average would be more accurate but requires census data).
"""

from province_mapping import PROVINCE_NAMES_2026

# ── 2022 GRDP per capita, old province codes (1–64) ──────────────────────────
# Units: million VND / person / year, current prices
# Code 64 (TP.HCM cum 2) shares the same economic zone as code 2
GRDP_2022_OLD: dict[int, float] = {
    1:  141.94,  # Ha Noi
    2:  157.54,  # TP.HCM
    3:  173.93,  # Hai Phong
    4:  101.41,  # Da Nang
    5:   33.54,  # Ha Giang
    6:   39.57,  # Cao Bang
    7:   47.47,  # Lai Chau
    8:   87.80,  # Lao Cai
    9:   51.16,  # Tuyen Quang
    10:  51.71,  # Lang Son
    11:  46.90,  # Bac Kan
    12: 111.65,  # Thai Nguyen
    13:  47.50,  # Yen Bai
    14:  48.55,  # Son La
    15:  39.70,  # Dien Bien
    16:  64.74,  # Hoa Binh
    17:  59.34,  # Phu Tho
    18: 127.80,  # Vinh Phuc
    19:  82.33,  # Bac Giang
    20: 198.78,  # Quang Ninh
    21: 163.82,  # Bac Ninh
    22:  86.54,  # Ha Nam
    23: 101.80,  # Hung Yen
    24:  87.25,  # Hai Duong
    25:  59.80,  # Thai Binh
    26:  48.98,  # Nam Dinh
    27:  80.86,  # Ninh Binh
    28:  67.81,  # Thanh Hoa
    29:  51.37,  # Nghe An
    30:  69.69,  # Ha Tinh
    31:  54.71,  # Quang Binh
    32:  62.74,  # Quang Tri
    33:  56.72,  # Thua Thien Hue
    34:  76.64,  # Quang Nam
    35:  97.40,  # Quang Ngai
    36:  70.70,  # Binh Dinh
    37:  57.96,  # Phu Yen
    38:  76.68,  # Khanh Hoa
    39:  77.62,  # Ninh Thuan
    40:  77.58,  # Binh Thuan
    41:  53.15,  # Kon Tum
    42:  53.45,  # Gia Lai
    43:  55.61,  # Dak Lak
    44:  59.60,  # Dak Nong
    45:  77.35,  # Lam Dong
    46:  85.38,  # Binh Phuoc
    47: 164.95,  # Binh Duong
    48: 132.98,  # Dong Nai
    49:  85.76,  # Tay Ninh
    50:  90.16,  # Long An
    51:  63.30,  # Tien Giang
    52:  49.05,  # Ben Tre
    53:  70.33,  # Tra Vinh
    54:  66.14,  # Vinh Long
    55:  62.00,  # Dong Thap
    56:  53.34,  # An Giang
    57:  66.37,  # Kien Giang
    58:  85.96,  # Can Tho
    59:  66.60,  # Hau Giang
    60:  54.77,  # Soc Trang
    61:  59.24,  # Bac Lieu
    62:  61.80,  # Ca Mau
    63: 335.47,  # Ba Ria – Vung Tau
    64: 157.54,  # TP.HCM (cum 2) — same economic zone as code 2
}

# ── 2026 merged provinces: simple average of constituent old-province GRDP ───
GRDP_2022_NEW: dict[int, float] = {}
for _new_code, (_name, _old_codes) in PROVINCE_NAMES_2026.items():
    vals = [GRDP_2022_OLD[c] for c in _old_codes if c in GRDP_2022_OLD]
    if vals:
        GRDP_2022_NEW[_new_code] = sum(vals) / len(vals)


def get_grdp_old(province_code: int) -> float | None:
    """GRDP per capita (million VND, 2022) for old exam province code (1-64)."""
    return GRDP_2022_OLD.get(province_code)


def get_grdp_2026(province_code: int) -> float | None:
    """GRDP per capita (million VND, 2022 base) for 2026 admin province code."""
    return GRDP_2022_NEW.get(province_code)


def add_grdp_column(df, year: int, province_col: str = 'province') -> None:
    """Add 'grdp_per_capita' column in-place (million VND, 2022 base prices)."""
    import pandas as pd

    if year == 2026:
        df['grdp_per_capita'] = df[province_col].apply(
            lambda p: get_grdp_2026(int(p)) if pd.notna(p) else None
        )
    else:
        df['grdp_per_capita'] = df[province_col].apply(
            lambda p: get_grdp_old(int(p)) if pd.notna(p) else None
        )
