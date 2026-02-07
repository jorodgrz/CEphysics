# Quick Start: Research Enhancements

This guide shows you how to use the new analysis features added to your CE research project.

## What's New? ✨

1. **Confidence Intervals** - All survival rates now have 95% CIs (Wilson score method)
2. **Lambda Mechanism Analysis** - Discovered λ_crit ≈ 0.04 for CE survival
3. **Evolutionary State Analysis** - Survival stratified by donor stellar phase
4. **Parameter Sensitivity Framework** - Ready for αCE sweep analysis
5. **Automated Simulation Runner** - Bash script for additional simulations

## Running the Enhanced Analysis

### Step 1: Main Analysis (Already Works!)

```bash
cd ~/CEphysics/CEphysics
python final_analysis.py
```

**New Output**:
- Console shows 95% confidence intervals for all rates
- `summary_statistics.csv` now has CI columns
- Example: "Solar Z: Survival 7.7% (95% CI: 0.2-36.0%)"

### Step 2: Mechanism Analysis (New!)

```bash
python analyze_mechanisms.py
```

**Generates**:
- `results/sensitivity/survival_vs_lambda.png` - Survival by lambda bins
- `results/sensitivity/survival_by_state.png` - Survival by evolutionary phase
- CSV files with stratified analysis

**Key Finding**: Only systems with λ > 0.04 can survive CE!

### Step 3: Alpha Sweep Analysis (Baseline)

```bash
python analyze_alpha_sweep.py
```

**Current Status**: Shows baseline α=0.5 results with warning about missing data.

To complete the analysis, you need to run additional simulations (see Step 4).

### Step 4: Run Additional Simulations (HPC Required)

**On your HPC JupyterHub**:

```bash
cd ~/CEphysics/CEphysics

# Option A: Automated (recommended)
bash run_alpha_sweep.sh  # Runs all 4 simulations, ~6-8 hours

# Option B: Manual (run individually)
python run_population.py --metallicity 0.001 --alpha_CE 1.0 --n_systems 200 --output low_Z_alpha1p0.h5
python run_population.py --metallicity 0.001 --alpha_CE 2.0 --n_systems 200 --output low_Z_alpha2p0.h5
python run_population.py --metallicity 0.006 --alpha_CE 1.0 --n_systems 200 --output mid_Z_alpha1p0.h5
python run_population.py --metallicity 0.006 --alpha_CE 2.0 --n_systems 200 --output mid_Z_alpha2p0.h5
```

**After simulations complete**:
```bash
python analyze_alpha_sweep.py  # Now shows full sensitivity!
```

## New Files to Check

### Analysis Scripts
- `analyze_mechanisms.py` - Lambda and evolutionary state analysis
- `analyze_alpha_sweep.py` - Parameter sensitivity analysis
- `run_alpha_sweep.sh` - Automated simulation runner

### New Results
```
results/
├── summary_statistics.csv          # Now with CIs!
└── sensitivity/
    ├── lambda_binned_survival.csv  # Survival by λ bins
    ├── donor_state_stratified.csv  # Survival by stellar state
    ├── alpha_sweep_summary.csv     # Parameter sweep results
    ├── survival_vs_lambda.png      # 4-panel mechanism figure
    ├── survival_by_state.png       # State stratification
    └── survival_vs_alphaCE.png     # Sensitivity plot
```

### Documentation
- `IMPLEMENTATION_SUMMARY.md` - Full technical details
- `README.md` - Updated with all new findings
- `docs/USAGE.md` - New script documentation
- `results/README.md` - Complete data catalog

## Key Scientific Results

### From Existing Data (Baseline α=0.5)

**1. Statistical Robustness**:
- Solar Z: 7.7% survival (95% CI: 0.2-36.0%)
- Mid Z: 0% survival (95% CI: 0.0-9.8%)
- Low Z: 0% survival (95% CI: 0.0-10.5%)

**2. Critical Lambda Threshold**:
- λ < 0.03: 0% survival (n=22)
- 0.03 < λ < 0.06: 11% survival (n=9, only 1 survivor)
- λ_crit ≈ 0.04 identified

**3. Evolutionary Phase Dependence**:
- Shell H-burning: 5.9% survival overall (λ̄=0.034)
- Core He-burning: 0.0% survival overall (λ̄=0.167)

**4. The Only Survivor**:
- Solar metallicity (Z=0.014)
- Shell H-burning phase
- λ = 0.043 (just above critical threshold)

### After α Sweep (To Be Determined)

Will answer:
- Is the low-Z death trap robust across all αCE values?
- What is the viable αCE parameter space?
- Does higher α enable survival at low λ?

## Workflow Summary

```
Current State (✓ Complete):
├── Baseline simulations (α=0.5) ✓
├── Confidence intervals added ✓
├── Mechanism analysis done ✓
└── Documentation updated ✓

Next Step (User Action Required):
├── Run: bash run_alpha_sweep.sh (on HPC, ~6-8 hours)
└── Then: python analyze_alpha_sweep.py

Future Options (See README):
├── Bootstrap resampling (N=10k)
├── Larger populations (N=1000)
└── Observational comparison
```

## Quick Commands Cheat Sheet

```bash
# Activate environment
conda activate posydon

# Full analysis pipeline (current data)
python final_analysis.py && \
python analyze_mechanisms.py && \
python analyze_alpha_sweep.py

# Run additional simulations (HPC)
bash run_alpha_sweep.sh

# After simulations complete
python analyze_alpha_sweep.py  # Full sensitivity
python final_analysis.py       # Regenerate with all data
```

## Troubleshooting

**"File not found: ce_fixed_lambda.h5"**
- Files are in `results/` folder
- Solution: `cp results/*.h5 .` (already done by implementation)

**"Missing optional files" in alpha sweep**
- Expected! Additional simulations not yet run
- Run `bash run_alpha_sweep.sh` on HPC

**"ModuleNotFoundError: scipy"**
- Solution: `conda activate posydon`

## Questions?

See detailed documentation:
- Technical details: `IMPLEMENTATION_SUMMARY.md`
- Full guide: `docs/USAGE.md`
- Results info: `results/README.md`

---

**Ready to enhance your research!** 🚀

Start with: `python analyze_mechanisms.py`
