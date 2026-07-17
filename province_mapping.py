"""
Province mapping for Vietnam exam data.

Two distinct code systems:
  - 2021-2025: sequential exam codes (01-64), old 63-province system
  - 2026+:     official administrative codes (01-96), new 34-province system

The 2025 province merger reduced 63 -> 34 provinces effective 2026 exam.
NOTE: merged-in lists are best-effort estimates; verify against official gazette.
"""

# ── OLD SYSTEM (2021–2025, exam SBD prefix, sequential 1-64) ─────────────────

PROVINCE_NAMES_OLD = {
    1:'Hà Nội', 2:'TP.HCM', 3:'Hải Phòng', 4:'Đà Nẵng',
    5:'Hà Giang', 6:'Cao Bằng', 7:'Lai Châu', 8:'Lào Cai',
    9:'Tuyên Quang', 10:'Lạng Sơn', 11:'Bắc Kạn', 12:'Thái Nguyên',
    13:'Yên Bái', 14:'Sơn La', 15:'Điện Biên', 16:'Hòa Bình',
    17:'Phú Thọ', 18:'Vĩnh Phúc', 19:'Bắc Giang', 20:'Quảng Ninh',
    21:'Bắc Ninh', 22:'Hà Nam', 23:'Hưng Yên', 24:'Hải Dương',
    25:'Thái Bình', 26:'Nam Định', 27:'Ninh Bình', 28:'Thanh Hóa',
    29:'Nghệ An', 30:'Hà Tĩnh', 31:'Quảng Bình', 32:'Quảng Trị',
    33:'Thừa Thiên Huế', 34:'Quảng Nam', 35:'Quảng Ngãi', 36:'Bình Định',
    37:'Phú Yên', 38:'Khánh Hòa', 39:'Ninh Thuận', 40:'Bình Thuận',
    41:'Kon Tum', 42:'Gia Lai', 43:'Đắk Lắk', 44:'Đắk Nông',
    45:'Lâm Đồng', 46:'Bình Phước', 47:'Bình Dương', 48:'Đồng Nai',
    49:'Tây Ninh', 50:'Long An', 51:'Tiền Giang', 52:'Bến Tre',
    53:'Trà Vinh', 54:'Vĩnh Long', 55:'Đồng Tháp', 56:'An Giang',
    57:'Kiên Giang', 58:'Cần Thơ', 59:'Hậu Giang', 60:'Sóc Trăng',
    61:'Bạc Liêu', 62:'Cà Mau', 63:'Bà Rịa-VT', 64:'TP.HCM (cụm 2)',
}

# Urban tiers — old system
URBAN_T1_OLD = {1, 2}
URBAN_T2_OLD = {3, 4, 33, 58}
CHUYEN_STRONG_OLD = {1, 2, 26, 29, 30, 3, 20, 28}

# Provinces implicated in 2018 fraud — confounds 2021 baseline
# Hà Giang=5, Sơn La=14, Hòa Bình=16
FRAUD_2018_OLD = {5, 14, 16}


# ── NEW SYSTEM (2026+, official administrative codes, 34 provinces) ──────────
#
# Format: code -> (display_name, [constituent_old_exam_codes])
# ⚠ = contains old fraud province territory

PROVINCE_NAMES_2026 = {
    1:  ('Hà Nội',               [1]),
    4:  ('Cao Bằng (merged)',    [5, 6, 11]),   # Hà Giang+Cao Bằng+Bắc Kạn ⚠
    8:  ('Tuyên Quang (merged)', [8, 9]),       # Lào Cai+Tuyên Quang
    11: ('Điện Biên (merged)',   [7, 15]),      # Lai Châu+Điện Biên
    12: ('Lai Châu',             [7]),          # unconfirmed standalone
    14: ('Sơn La (merged)',      [14, 16]),     # Sơn La+Hòa Bình ⚠
    15: ('Yên Bái (merged)',     [13]),
    19: ('Thái Nguyên (merged)', [12]),          # Thái Nguyên (Lạng Sơn kept separate)
    20: ('Lạng Sơn',            [10]),
    22: ('Quảng Ninh',          [20]),
    24: ('Bắc Giang (merged)',  [19, 21]),      # Bắc Giang+Bắc Ninh
    25: ('Phú Thọ (merged)',    [17, 18]),      # Phú Thọ+Vĩnh Phúc
    31: ('Hải Phòng (merged)',  [3, 23, 24]),   # Hải Phòng+Hưng Yên+Hải Dương
    33: ('Hưng Yên (merged)',   [23]),
    37: ('Ninh Bình (merged)',  [22, 25, 26, 27]),  # Hà Nam+Thái Bình+Nam Định+Ninh Bình
    38: ('Thanh Hóa',          [28]),
    40: ('Nghệ An (merged)',    [29, 30]),      # Nghệ An+Hà Tĩnh
    42: ('Hà Tĩnh',            [30]),
    44: ('Quảng Bình (merged)', [31, 32]),      # Quảng Bình+Quảng Trị
    46: ('Thừa Thiên Huế',     [33]),
    48: ('Đà Nẵng (merged)',   [4, 34]),        # Đà Nẵng+Quảng Nam
    51: ('Quảng Ngãi (merged)',[35]),
    52: ('Bình Định (merged)', [36, 37]),       # Bình Định+Phú Yên
    56: ('Khánh Hòa (merged)', [38, 39]),       # Khánh Hòa+Ninh Thuận
    66: ('Đắk Lắk (merged)',   [42, 43, 44]),   # Gia Lai+Đắk Lắk+Đắk Nông
    68: ('Lâm Đồng (merged)',  [40, 45]),       # Bình Thuận+Lâm Đồng
    75: ('Đồng Nai (merged)',  [41, 46, 48, 49, 63]),  # Kon Tum+Bình Phước+Đồng Nai+Tây Ninh+Bà Rịa-VT
    79: ('TP.HCM (merged)',    [2, 47, 64]),    # TP.HCM+Bình Dương
    80: ('Long An',            [50]),
    82: ('Tiền Giang (merged)',[51, 52]),       # Tiền Giang+Bến Tre
    86: ('Vĩnh Long (merged)', [53, 54, 55]),   # Trà Vinh+Vĩnh Long+Đồng Tháp
    91: ('Kiên Giang (merged)',[56, 57]),       # An Giang+Kiên Giang
    92: ('Cần Thơ (merged)',   [58, 59, 60, 61]),  # Cần Thơ+Hậu Giang+Sóc Trăng+Bạc Liêu
    96: ('Cà Mau',             [62]),
}

PROVINCE_DISPLAY_2026 = {k: v[0] for k, v in PROVINCE_NAMES_2026.items()}

# Urban tiers — new system
URBAN_T1_2026 = {1, 79}
URBAN_T2_2026 = {31, 48, 46, 92}

# New provinces whose merged territory includes old fraud provinces (5, 14, 16)
FRAUD_ADJACENT_2026 = {4, 14}

# Fee-exempt provinces (Ha Noi, TP.HCM, Hai Phong)
FEE_EXEMPT_OLD  = {1, 2, 3}
FEE_EXEMPT_2026 = {1, 79, 31}

# Chuyen-strong provinces in each code system
CHUYEN_STRONG_OLD  = {1, 2, 26, 29, 30, 3, 20, 28}
# Computed after OLD_TO_NEW_2026 is built (see below)

# Crosswalk: old exam code -> new 2026 admin code
OLD_TO_NEW_2026: dict[int, int] = {}
for _new, (_name, _olds) in PROVINCE_NAMES_2026.items():
    for _old in _olds:
        OLD_TO_NEW_2026[_old] = _new

CHUYEN_STRONG_2026 = {OLD_TO_NEW_2026[c] for c in CHUYEN_STRONG_OLD if c in OLD_TO_NEW_2026}
# = {1, 22, 31, 37, 38, 40, 42, 79}


# ── Helpers ───────────────────────────────────────────────────────────────────

def urban_tier_old(code: int) -> str:
    if code in URBAN_T1_OLD: return 'Đô thị lớn'
    if code in URBAN_T2_OLD: return 'Đô thị vừa'
    return 'Tỉnh lẻ/Nông thôn'


def urban_tier_2026(code: int) -> str:
    if code in URBAN_T1_2026: return 'Đô thị lớn'
    if code in URBAN_T2_2026: return 'Đô thị vừa'
    return 'Tỉnh lẻ/Nông thôn'


def get_name_old(code: int) -> str:
    return PROVINCE_NAMES_OLD.get(code, f'Unknown({code})')


def get_name_2026(code: int) -> str:
    return PROVINCE_DISPLAY_2026.get(code, f'Unknown({code})')


def remap_old_to_2026(df, province_col: str = 'province') -> 'pd.Series':
    """Map old exam province codes to 2026 admin codes. Returns new series."""
    import pandas as pd
    return df[province_col].map(OLD_TO_NEW_2026)
