#!/bin/bash
#
# Alpha Sweep Simulation Runner
# 
# This script runs the additional αCE sensitivity simulations needed
# to complete the parameter robustness analysis.
#
# Usage: bash run_alpha_sweep.sh
#
# Runtime: ~6-8 hours total on HPC (4 simulations × ~90 minutes each)
#

set -e  # Exit on error

echo "============================================================"
echo "αCE SENSITIVITY SIMULATIONS"
echo "============================================================"
echo ""
echo "This will run 4 additional population synthesis simulations:"
echo "  • Low Z (0.001): α = 1.0, 2.0"
echo "  • Mid Z (0.006): α = 1.0, 2.0"
echo ""
echo "Each simulation: 200 systems, ~90 minutes"
echo "Total runtime: ~6-8 hours"
echo ""
echo "Press Ctrl+C to cancel, or Enter to continue..."
read

# Check if base simulations exist
if [ ! -f "ce_fixed_lambda.h5" ] && [ ! -f "results/ce_fixed_lambda.h5" ]; then
    echo "⚠ WARNING: Base simulation files not found!"
    echo "Please run the baseline simulations first:"
    echo "  python run_population.py --metallicity 0.014 --alpha_CE 0.5 --n_systems 200 --output ce_fixed_lambda.h5"
    echo "  python run_population.py --metallicity 0.006 --alpha_CE 0.5 --n_systems 200 --output mid_Z_lambda.h5"
    echo "  python run_population.py --metallicity 0.001 --alpha_CE 0.5 --n_systems 200 --output low_Z_lambda.h5"
    exit 1
fi

echo ""
echo "============================================================"
echo "Starting simulations..."
echo "============================================================"
echo ""

# Low metallicity, α = 1.0
echo "[1/4] Running Low Z (0.001), α = 1.0..."
python run_population.py \
    --M1_min 10 --M1_max 20 --M1_samples 10 \
    --M2_min 8 --M2_max 15 --M2_samples 10 \
    --P_min 50 --P_max 500 --P_samples 20 \
    --metallicity 0.001 \
    --alpha_CE 1.0 \
    --n_systems 200 \
    --output low_Z_alpha1p0.h5
echo "✓ Complete"
echo ""

# Low metallicity, α = 2.0
echo "[2/4] Running Low Z (0.001), α = 2.0..."
python run_population.py \
    --M1_min 10 --M1_max 20 --M1_samples 10 \
    --M2_min 8 --M2_max 15 --M2_samples 10 \
    --P_min 50 --P_max 500 --P_samples 20 \
    --metallicity 0.001 \
    --alpha_CE 2.0 \
    --n_systems 200 \
    --output low_Z_alpha2p0.h5
echo "✓ Complete"
echo ""

# Mid metallicity, α = 1.0
echo "[3/4] Running Mid Z (0.006), α = 1.0..."
python run_population.py \
    --M1_min 10 --M1_max 20 --M1_samples 10 \
    --M2_min 8 --M2_max 15 --M2_samples 10 \
    --P_min 50 --P_max 500 --P_samples 20 \
    --metallicity 0.006 \
    --alpha_CE 1.0 \
    --n_systems 200 \
    --output mid_Z_alpha1p0.h5
echo "✓ Complete"
echo ""

# Mid metallicity, α = 2.0
echo "[4/4] Running Mid Z (0.006), α = 2.0..."
python run_population.py \
    --M1_min 10 --M1_max 20 --M1_samples 10 \
    --M2_min 8 --M2_max 15 --M2_samples 10 \
    --P_min 50 --P_max 500 --P_samples 20 \
    --metallicity 0.006 \
    --alpha_CE 2.0 \
    --n_systems 200 \
    --output mid_Z_alpha2p0.h5
echo "✓ Complete"
echo ""

echo "============================================================"
echo "ALL SIMULATIONS COMPLETE!"
echo "============================================================"
echo ""
echo "Generated files:"
echo "  • low_Z_alpha1p0.h5"
echo "  • low_Z_alpha2p0.h5"
echo "  • mid_Z_alpha1p0.h5"
echo "  • mid_Z_alpha2p0.h5"
echo ""
echo "Next steps:"
echo "  1. Run full sensitivity analysis:"
echo "     python analyze_alpha_sweep.py"
echo ""
echo "  2. Update figures with complete results"
echo ""
echo "  3. Check results/sensitivity/ for outputs"
echo ""
echo "============================================================"
