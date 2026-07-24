"""
Portable configuration for PTDLTM project.
Uses relative paths — works across devices.
"""

from pathlib import Path
import sys

# Root of project (this file's directory)
PROJECT_ROOT = Path(__file__).parent.absolute()

# Data directories (relative to project root)
DATA_BASE = PROJECT_ROOT / 'GraduationExamScoreProcessing' / 'Results'
OUTPUT_DIR = PROJECT_ROOT / 'figures'
REPORT_DIR = PROJECT_ROOT / 'report'

# Create output directories if missing
OUTPUT_DIR.mkdir(exist_ok=True)
REPORT_DIR.mkdir(exist_ok=True)

# Validate data directory exists
if not DATA_BASE.exists():
    raise FileNotFoundError(
        f"Data directory not found: {DATA_BASE}\n"
        f"Ensure GraduationExamScoreProcessing/Results/ exists in project root"
    )

# Convert to strings for backward compatibility with existing scripts
BASE = str(DATA_BASE)
OUT = str(OUTPUT_DIR)

# Python path for imports
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

__all__ = ['PROJECT_ROOT', 'DATA_BASE', 'OUTPUT_DIR', 'REPORT_DIR', 'BASE', 'OUT']
