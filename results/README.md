# Results Directory

This directory contains all analysis outputs from the CE metallicity study.

## Data Files

### HDF5 Files (Binary Evolution Data)

**Baseline Simulations** (α_CE = 0.5):
- `ce_fixed_lambda.h5` - Solar metallicity (Z=0.014), 200 systems
- `mid_Z_lambda.h5` - Mid metallicity (Z=0.006), 200 systems
- `low_Z_lambda.h5` - Low metallicity (Z=0.001), 200 systems

**Sensitivity Simulations** (α_CE sweep - to be generated):
- `low_Z_alpha1p0.h5` - Low Z, α=1.0, 200 systems
- `low_Z_alpha2p0.h5` - Low Z, α=2.0, 200 systems
- `mid_Z_alpha1p0.h5` - Mid Z, α=1.0, 200 systems
- `mid_Z_alpha2p0.h5` - Mid Z, α=2.0, 200 systems

Each HDF5 file contains a pandas DataFrame with columns:
- Initial conditions: `M1_initial`, `M2_initial`, `P_initial`
- Simulation results: `CE_occurred`, `survived_CE`, `lambda_CE`, `donor_state`
- Final state information

### CSV Files (Processed Results)

**Main Results**:
- `summary_statistics.csv` - Aggregate statistics with 95% confidence intervals
- `solar_Z_results.csv` - Complete results for solar metallicity
- `mid_Z_results.csv` - Complete results for mid metallicity
- `low_Z_results.csv` - Complete results for low metallicity

**Sensitivity Analysis** (in `sensitivity/` subdirectory):
- `lambda_binned_survival.csv` - Survival rates by lambda bins with CIs
- `donor_state_stratified.csv` - Survival by evolutionary state
- `alpha_sweep_summary.csv` - Parameter sensitivity results

## Figures

### Main Results
- `lambda_vs_metallicity.png` - Lambda trend and survival rates vs metallicity (Figure 1)
- `detailed_comparison.png` - 4-panel comprehensive comparison (Figure 2)

### Mechanism Analysis (`sensitivity/` subdirectory)
- `survival_vs_lambda.png` - Survival probability vs lambda bins (with 95% CIs)
- `survival_by_state.png` - Survival stratified by donor evolutionary state
- `survival_vs_alphaCE.png` - Parameter sensitivity plot (baseline α=0.5 shown)

## Summary Statistics

Key findings from `summary_statistics.csv` (with 95% confidence intervals):

| Metallicity | Total Systems | CE Events (95% CI) | Survival Rate (95% CI) | Mean Lambda |
|------------|---------------|-----------|---------------|-------------|
| Solar (0.014) | 200 | 6.5% (3.5-10.9%) | 7.7% (0.2-36.0%) | 0.144 ± 0.097 |
| Mid (0.006) | 200 | 14.5% (9.9-20.2%) | 0.0% (0.0-9.8%) | 0.111 ± 0.114 |
| Low (0.001) | 200 | 13.5% (9.1-19.0%) | 0.0% (0.0-10.5%) | 0.111 ± 0.114 |

**Critical Finding**: λ_crit ≈ 0.04 identified as minimum lambda for CE survival.

## Regenerating Results

### Baseline Analysis (Current Data)

```bash
# From project root
python final_analysis.py           # Main figures with CIs
python analyze_mechanisms.py       # Lambda binning and state analysis
python analyze_alpha_sweep.py      # Baseline α=0.5 only (warns about missing data)
```

### Complete Analysis (After Additional Simulations)

First run the α_CE sweep simulations:
```bash
bash run_alpha_sweep.sh  # Runs 4 additional simulations (~6-8 hours)
```

Then regenerate all analyses:
```bash
python final_analysis.py           # Updated with CIs
python analyze_mechanisms.py       # Mechanism analysis
python analyze_alpha_sweep.py      # Full parameter sensitivity
```

## Statistical Methods

- **Confidence Intervals**: Wilson score method (Clopper-Pearson) for binomial proportions
- **Small Sample Correction**: Beta distribution used for exact CIs when k=0 or k=n
- **"Rule of 3"**: When 0 survivors, 95% upper bound = 3/N ≈ 1.5% for N=200

## Data Format

### HDF5 Structure
Pandas DataFrames with columns:
- `M1_initial`, `M2_initial`, `P_initial` - Initial binary parameters
- `CE_occurred` - Boolean, whether CE event occurred
- `lambda_CE` - Envelope binding energy parameter (from MESA grids)
- `donor_state` - Stellar evolutionary state at CE (e.g., H-rich_Shell_H_burning)
- `survived_CE` - Boolean, whether binary survived CE without merging
- Additional final state properties

### CSV Format
Same structure as HDF5, readable in Excel/LibreOffice.

## Citation

If you use this data, please cite:
- POSYDON: Fragos et al. (2023), ApJS 264, 45
- This work: Rodriguez (2026), [In preparation]

## Contact

For questions about this data: jrodriguezruelas@ucsd.edu
