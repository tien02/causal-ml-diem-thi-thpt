#!/bin/bash
# Zero-effort setup script — clone, run, done.
# Usage: ./setup.sh

set -e

echo "🔧 PTDLTM Setup"
echo "================="

# 1. Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Install Python 3.9+"
    exit 1
fi
echo "✓ Python $(python3 --version | cut -d' ' -f2)"

# 2. Check git-lfs
if ! command -v git-lfs &> /dev/null; then
    echo "⚠️  git-lfs not installed. Large files won't download automatically."
    echo "   Install: apt install git-lfs (Linux) | brew install git-lfs (macOS)"
else
    echo "✓ Git LFS installed"
    git lfs install
fi

# 3. Install Python dependencies
echo ""
echo "📦 Installing dependencies..."
pip install -q pandas numpy matplotlib seaborn scipy scikit-learn statsmodels networkx
pip install -q econml dowhy 2>/dev/null || echo "   (econml/dowhy optional; continuing without)"

echo "✓ Dependencies installed"

# 4. Verify data structure
echo ""
echo "📂 Verifying data directory..."
if [ ! -d "GraduationExamScoreProcessing/Results" ]; then
    echo "❌ Data directory not found:"
    echo "   Expected: GraduationExamScoreProcessing/Results/"
    echo ""
    echo "   If cloned without git-lfs:"
    echo "     1. Install git-lfs: https://git-lfs.github.com"
    echo "     2. git lfs pull"
    exit 1
fi

csv_count=$(find GraduationExamScoreProcessing/Results -name "*.csv" -type f | wc -l)
if [ "$csv_count" -lt 5 ]; then
    echo "⚠️  Only $csv_count CSV files found (expected 5+)"
    echo "   Run: git lfs pull"
else
    echo "✓ Data files present ($csv_count CSV)"
fi

# 5. Ready
echo ""
echo "🚀 Ready to run!"
echo ""
echo "Next steps:"
echo "  python analysis.py           # Descriptive stats + DiD"
echo "  python fraud_detection.py    # Anomaly detection"
echo "  python causal_ml.py          # RDD + Double ML"
echo "  python synthetic_control.py  # Synthetic Control + EconML"
echo "  python dowhy_refutation.py   # DoWhy DAG"
echo ""
echo "See SETUP.md for detailed instructions."
