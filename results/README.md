# Results Directory

This directory contains all outputs from the CE metallicity study.

## Data Files

### HDF5 Files (Binary Evolution Histories)
- `ce_fixed_lambda.h5` - Solar metallicity (Z = 0.014), 200 systems
- `mid_Z_lambda.h5` - Mid metallicity (Z = 0.006), 200 systems  
- `low_Z_lambda.h5` - Low metallicity (Z = 0.001), 200 systems

### CSV Files (Exported Results)
- `solar_Z_results.csv` - Solar Z data in table format
- `mid_Z_results.csv` - Mid Z data in table format
- `low_Z_results.csv` - Low Z data in table format
- `summary_statistics.csv` - Aggregate statistics across all metallicities

## Figures

### Main Results
- `lambda_vs_metallicity.png` - **Figure 1**: Lambda trend and critical threshold
  * Left: Lambda vs metallicity with error bars
  * Right: Survival rate showing death trap transition

- `detailed_comparison.png` - **Figure 2**: Comprehensive 4-panel comparison
  * Top left: Lambda distributions by metallicity
  * Top right: CE occurrence vs survival rates
  * Bottom left: Lambda by stellar state
  * Bottom right: Summary text box

## Summary Statistics

Key findings from `summary_statistics.csv`:

| Metallicity | CE Rate | Survival | Mean λ |
|------------|---------|----------|--------|
| Z = 0.014  | 6.5%    | 7.7%     | 0.144  |
| Z = 0.006  | 14.5%   | 0.0%     | 0.111  |
| Z = 0.001  | 13.5%   | 0.0%     | 0.111  |

## Generating Results

To regenerate all figures and statistics:

```bash
cd ~/CEphysics
python final_analysis.py
```

This script will:
1. Load all three metallicity datasets
2. Calculate summary statistics
3. Generate publication-quality figures
4. Export CSV files
5. Copy HDF5 files to results/

## Data Format

### HDF5 Structure
Pandas DataFrames with columns:
- `M1_initial`, `M2_initial`, `P_initial`, `Z`, `q_initial` - Initial conditions
- `CE_occurred` - Boolean, whether CE happened
- `lambda_CE` - Envelope binding energy parameter
- `donor_state` - Stellar evolutionary state at CE
- `survived_CE` - Boolean, whether binary survived CE
- `final_M1`, `final_M2`, `final_P`, `final_state` - Final properties

### CSV Format
Same structure as HDF5, readable in Excel/LibreOffice

## Citation

If you use this data, please cite:
- POSYDON: Fragos et al. (2023), ApJS 264, 45
- This work: [Your paper reference]

## Contact

For questions about this data, contact: [Your email]
