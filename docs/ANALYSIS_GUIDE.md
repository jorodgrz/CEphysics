# CEphysics Analysis Pipeline Guide

This guide explains the new modular analysis pipeline for completing publication-ready analyses.

## Overview

The project now has **4 comprehensive analysis scripts** that replace the old bash workflow:

1. **`alpha_sweep.py`** - Unified simulation runner with error recovery
2. **`bootstrap_analysis.py`** - Statistical robustness via resampling
3. **`physics_analysis.py`** - Detailed mechanism investigation
4. **`observational_comparison.py`** - Astrophysical context

## Quick Start

### Complete Analysis in 4 Commands

```bash
# 1. Run alpha sweep simulations (6-8 hours, 4 sims × 90 min)
python scripts/alpha_sweep.py --yes --analyze

# 2. Bootstrap resampling for robust uncertainties (15-30 min)
python scripts/bootstrap_analysis.py

# 3. Detailed physics mechanisms (5-10 min)
python scripts/physics_analysis.py --include-alpha

# 4. Observational comparison (2-5 min)
python scripts/observational_comparison.py
```

**Total time**: ~7-9 hours (mostly automated)

---

## Detailed Script Documentation

### 1. Alpha Sweep Runner (`alpha_sweep.py`)

**Purpose**: Run the 4 additional αCE simulations needed for parameter robustness analysis.

**Features**:
- ✅ Checkpointing (skip completed simulations)
- ✅ Error recovery (continue on failure)
- ✅ Progress tracking with detailed logs
- ✅ HDF5 file validation
- ✅ Automatic analysis integration

**Usage**:

```bash
# Basic usage (with confirmation prompt)
python scripts/alpha_sweep.py

# Skip confirmation prompt
python scripts/alpha_sweep.py --yes

# Resume from checkpoint (skip completed sims)
python scripts/alpha_sweep.py --resume

# Run analysis after simulations
python scripts/alpha_sweep.py --analyze

# Skip simulations, only run analysis
python scripts/alpha_sweep.py --analyze-only

# See what would run without executing
python scripts/alpha_sweep.py --dry-run

# Stop on first error (default: continue)
python scripts/alpha_sweep.py --stop-on-error
```

**Simulations**:
1. Low Z (0.001), α=1.0 → `low_Z_alpha1p0.h5`
2. Low Z (0.001), α=2.0 → `low_Z_alpha2p0.h5`
3. Mid Z (0.006), α=1.0 → `mid_Z_alpha1p0.h5`
4. Mid Z (0.006), α=2.0 → `mid_Z_alpha2p0.h5`

**Outputs**:
- `alpha_sweep.log` - Detailed execution log
- `alpha_sweep_progress.json` - Checkpoint file
- `*.h5` - Simulation results
- Analysis outputs (if `--analyze` used)

**Runtime**: ~6-8 hours total (~90 min per simulation)

---

### 2. Bootstrap Analysis (`bootstrap_analysis.py`)

**Purpose**: Provide robust statistical uncertainty estimates via bootstrap resampling.

**Why Bootstrap?**
- Non-parametric (no distributional assumptions)
- Robust for small samples
- Captures full uncertainty including correlations
- Publication-standard methodology

**Usage**:

```bash
# Default: 10,000 iterations
python scripts/bootstrap_analysis.py

# Faster (less precise)
python scripts/bootstrap_analysis.py --n_boot 5000

# More precise (slower)
python scripts/bootstrap_analysis.py --n_boot 20000
```

**Analyses**:
1. CE occurrence rates with bootstrap CIs
2. CE survival rates with bootstrap CIs
3. Lambda distributions with uncertainties
4. Survival vs lambda (binned) with CIs

**Outputs**:
- `results/bootstrap/ce_rates_bootstrap.csv`
- `results/bootstrap/survival_rates_bootstrap.csv`
- `results/bootstrap/lambda_bootstrap.csv`
- `results/bootstrap/survival_vs_lambda_bootstrap.csv`
- `results/bootstrap/bootstrap_analysis.png` (4-panel figure)

**Runtime**: ~15-30 minutes (depends on `n_boot`)

---

### 3. Physics Analysis (`physics_analysis.py`)

**Purpose**: In-depth investigation of CE physics mechanisms.

**Analyses**:
1. **Shell vs Core burning donors**
   - Survival rates by evolutionary phase
   - Lambda distributions by donor type
   
2. **Mass ratio dependence**
   - Survival as f(q = M₂/M₁)
   - Binned analysis with CIs
   
3. **Orbital period dependence**
   - Survival as f(P_initial)
   - Log-spaced bins
   
4. **2D survival maps**
   - Heat maps of survival probability
   - f(q, P) for each metallicity
   
5. **Binding energy correlations**
   - Lambda by donor type and metallicity

**Usage**:

```bash
# Baseline analysis only
python scripts/physics_analysis.py

# Include alpha sweep data
python scripts/physics_analysis.py --include-alpha
```

**Outputs**:
- `results/physics/shell_vs_core_analysis.csv`
- `results/physics/survival_vs_mass_ratio.csv`
- `results/physics/survival_vs_period.csv`
- `results/physics/2d_survival_maps.png`
- `results/physics/physics_analysis.png`

**Runtime**: ~5-10 minutes

---

### 4. Observational Comparison (`observational_comparison.py`)

**Purpose**: Compare simulation results to observations and discuss astrophysical implications.

**Includes**:

1. **Galactic DNS Metallicity Distribution**
   - 7 known systems with metallicity estimates
   - Mean Z = 0.013 ± 0.002
   - All systems have Z > 0.010
   
2. **LIGO/Virgo Merger Rates**
   - BNS merger rate: 10-1700 Gpc⁻³ yr⁻¹
   - Redshift-dependent implications
   
3. **Cosmic Star Formation History**
   - Metallicity evolution: Z(z)
   - Critical redshift z_crit ≈ 0.3-0.5
   
4. **DNS Formation Channels**
   - CE channel constraints
   - Alternative channel requirements
   - Channel-switching at z_crit

**Usage**:

```bash
# Standard run
python scripts/observational_comparison.py

# Verbose output
python scripts/observational_comparison.py --verbose
```

**Outputs**:
- `results/observational/galactic_dns_metallicities.csv`
- `results/observational/metallicity_evolution.csv`
- `results/observational/simulation_summary.csv`
- `results/observational/observational_comparison.png` (multi-panel figure)

**Runtime**: ~2-5 minutes

---

## Workflow Recommendations

### For Quick Results (Already Have Baseline Data)

If you already have `ce_fixed_lambda.h5`, `mid_Z_lambda.h5`, `low_Z_lambda.h5`:

```bash
# 1. Statistical robustness
python scripts/bootstrap_analysis.py

# 2. Physics mechanisms
python scripts/physics_analysis.py

# 3. Observational context
python scripts/observational_comparison.py
```

**Time**: ~20-45 minutes

### For Complete Analysis (Need Alpha Sweep)

```bash
# 1. Run simulations (long!)
python scripts/alpha_sweep.py --yes --analyze

# 2. Bootstrap
python scripts/bootstrap_analysis.py

# 3. Physics (include alpha data)
python scripts/physics_analysis.py --include-alpha

# 4. Observations
python scripts/observational_comparison.py
```

**Time**: ~7-9 hours (mostly simulation time)

### For Publication Figures

All scripts generate publication-quality figures automatically:
- 300 DPI resolution
- Clear labels and legends
- Consistent color schemes
- Error bars and confidence intervals

Figures are saved in:
- `results/` - Main results
- `results/bootstrap/` - Bootstrap analysis
- `results/physics/` - Physics mechanisms
- `results/observational/` - Observational comparison
- `results/sensitivity/` - Alpha sweep sensitivity

---

## Error Handling

### If a Simulation Fails

The `alpha_sweep.py` script handles failures gracefully:

1. **Logs the error** to `alpha_sweep.log`
2. **Saves checkpoint** with failure status
3. **Continues to next simulation** (unless `--stop-on-error`)
4. **Reports summary** at end

To retry failed simulations:
```bash
# Edit checkpoint file to remove failed entry
# OR delete the invalid .h5 file
python scripts/alpha_sweep.py --resume
```

### If Analysis Fails

Check prerequisites:
```bash
# Bootstrap needs baseline data
ls ce_fixed_lambda.h5 mid_Z_lambda.h5 low_Z_lambda.h5

# Physics analysis needs CE events
python -c "import pandas as pd; print(pd.read_hdf('ce_fixed_lambda.h5').shape)"

# Observational comparison needs all three
ls ce_fixed_lambda.h5 mid_Z_lambda.h5 low_Z_lambda.h5
```

---

## Output Summary

After running all scripts, you'll have:

### CSV Data Files (17 files)
- Summary statistics
- Bootstrap distributions
- Physics analysis results
- Observational data
- Sensitivity analysis

### Figures (10+ figures)
- Lambda vs metallicity
- Detailed comparison
- Bootstrap analysis (4 panels)
- Physics analysis (4 panels)
- 2D survival maps
- Observational comparison (6 panels)
- Sensitivity analysis (2+ panels)

### Logs and Checkpoints
- `alpha_sweep.log` - Execution log
- `alpha_sweep_progress.json` - Checkpoint

---

## Tips and Best Practices

### 1. Run Simulations Overnight
Alpha sweep takes 6-8 hours - perfect for overnight runs:
```bash
nohup python scripts/alpha_sweep.py --yes --analyze > alpha_sweep_output.txt 2>&1 &
```

### 2. Check Progress
```bash
# View live log
tail -f alpha_sweep.log

# Check checkpoint
cat alpha_sweep_progress.json
```

### 3. Validate Outputs
```bash
# Check HDF5 files
python -c "
import pandas as pd
for f in ['low_Z_alpha1p0.h5', 'low_Z_alpha2p0.h5', 
          'mid_Z_alpha1p0.h5', 'mid_Z_alpha2p0.h5']:
    try:
        df = pd.read_hdf(f, 'results')
        print(f'{f}: {len(df)} systems ✓')
    except:
        print(f'{f}: INVALID ✗')
"
```

### 4. Modular Execution
Run analyses independently as needed:
```bash
# Just bootstrap
python scripts/bootstrap_analysis.py --n_boot 20000

# Just physics with alpha data
python scripts/physics_analysis.py --include-alpha

# Just observations
python scripts/observational_comparison.py --verbose
```

---

## Citation and References

If you use these scripts in your research, please cite:

- **POSYDON**: Fragos et al. (2023)
- **Bootstrap methodology**: Efron & Tibshirani (1993)
- **Galactic DNS data**: Tauris et al. (2017), Andrews et al. (2015)
- **LIGO/Virgo rates**: Abbott et al. (2021) - GWTC-3
- **Cosmic SFR**: Madau & Dickinson (2014)

---

## Support

For issues or questions:
1. Check `alpha_sweep.log` for errors
2. Validate input files exist and are valid
3. Check POSYDON environment is activated
4. Review error messages in output

Common issues:
- **"File not found"**: Run baseline simulations first
- **"No CE events"**: Check simulation parameters
- **"Import error"**: Activate POSYDON environment
- **"Memory error"**: Reduce `n_boot` for bootstrap

---

## What's Next?

After completing these analyses, you'll have:

✅ Complete αCE sensitivity analysis  
✅ Robust statistical uncertainties (bootstrap)  
✅ Detailed physics mechanism understanding  
✅ Observational context and implications  

**Ready for publication!** 🎉

Consider adding:
- [ ] Triple interaction channel comparison
- [ ] N=1000 population for tighter constraints
- [ ] Recombination energy toggle tests
- [ ] Additional metallicity values
