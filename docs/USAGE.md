# Usage Guide

How to run population synthesis and analyze results.

## Quick Start

### 1. Activate Environment
```bash
conda activate posydon
cd ~/CEphysics/CEphysics
```

### 2. Run Population Synthesis
Start with a small test run:
```bash
python run_population.py --n_systems 10 --output test.h5
```

## Running Population Synthesis

### Basic Usage

```bash
python run_population.py --n_systems 200 --output results.h5
```

### With Custom Parameters

```bash
python run_population.py \
  --M1_min 10 --M1_max 20 --M1_samples 10 \
  --M2_min 8 --M2_max 15 --M2_samples 10 \
  --P_min 50 --P_max 500 --P_samples 20 \
  --metallicity 0.014 \
  --alpha_CE 0.5 \
  --n_systems 200 \
  --output solar_Z.h5
```

### Multiple Metallicities

Run each metallicity separately:

```bash
# Solar metallicity
python run_population.py --metallicity 0.014 --n_systems 200 --alpha_CE 0.5 --output solar_Z.h5

# Mid metallicity
python run_population.py --metallicity 0.006 --n_systems 200 --alpha_CE 0.5 --output mid_Z.h5

# Low metallicity
python run_population.py --metallicity 0.001 --n_systems 200 --alpha_CE 0.5 --output low_Z.h5
```

**Runtime**: ~3-5 minutes per 200 systems (after initial step loading)

## Analyzing Results

### Automated Analysis

#### 1. Main Analysis (with Confidence Intervals)

Generate all figures and statistics:

```bash
python final_analysis.py
```

This creates in `results/`:
- `lambda_vs_metallicity.png` - Main result figure
- `detailed_comparison.png` - 4-panel comparison
- `summary_statistics.csv` - Aggregate statistics with 95% CIs
- `*_results.csv` - Individual metallicity datasets

#### 2. Mechanism Analysis

Analyze survival probability vs lambda and evolutionary state:

```bash
python analyze_mechanisms.py
```

This creates in `results/sensitivity/`:
- `survival_vs_lambda.png` - Survival probability by lambda bins (with CIs)
- `survival_by_state.png` - Survival stratified by donor evolutionary state
- `lambda_binned_survival.csv` - Binned survival data
- `donor_state_stratified.csv` - State-specific survival rates

**Key output**: Identifies λ_crit ≈ 0.04 as minimum lambda for survival.

#### 3. Parameter Sensitivity Analysis

Test robustness across αCE values:

```bash
python analyze_alpha_sweep.py
```

This creates in `results/sensitivity/`:
- `survival_vs_alphaCE.png` - Survival rate vs CE efficiency parameter
- `alpha_sweep_summary.csv` - Full parameter sweep results

**Note**: Requires additional simulation runs at α=1.0 and α=2.0 for complete analysis (see Future Work in main README).

### Interactive Analysis

Use the Jupyter notebook:

```bash
jupyter notebook Analysis.ipynb
```

The notebook contains:
- Data loading and inspection
- Custom plotting code
- Statistical analysis
- Parameter exploration

## Command Reference

### run_population.py

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--M1_min`, `--M1_max` | Primary mass range (M☉) | 8.0, 20.0 |
| `--M1_samples` | Number of M1 samples | 10 |
| `--M2_min`, `--M2_max` | Secondary mass range (M☉) | 8.0, 20.0 |
| `--M2_samples` | Number of M2 samples | 10 |
| `--P_min`, `--P_max` | Period range (days) | 100, 5000 |
| `--P_samples` | Number of period samples | 10 |
| `--metallicity` | Metallicity value(s) | 0.014 |
| `--alpha_CE` | CE efficiency parameter | 1.0 |
| `--n_systems` | Random sample size | None (all) |
| `--output` | Output HDF5 file | CE_results.h5 |
| `--quiet` | Suppress progress output | False |

### Example Workflows

#### Quick Test (5 systems)
```bash
python run_population.py --n_systems 5 --output test.h5
```

#### Production Run (Solar Z)
```bash
python run_population.py \
  --metallicity 0.014 \
  --n_systems 200 \
  --alpha_CE 0.5 \
  --output solar_Z.h5
```

#### Full Metallicity Study
```bash
# Run all three
python run_population.py --metallicity 0.001 --n_systems 200 --alpha_CE 0.5 --output low_Z.h5
python run_population.py --metallicity 0.006 --n_systems 200 --alpha_CE 0.5 --output mid_Z.h5
python run_population.py --metallicity 0.014 --n_systems 200 --alpha_CE 0.5 --output solar_Z.h5

# Generate analysis
python final_analysis.py
```

## Working with Results

### Python Analysis

```python
import pandas as pd

# Load results
df = pd.read_hdf('solar_Z.h5', 'results')

# Filter CE systems
ce_systems = df[df['CE_occurred'] == True]

# Get lambda values
lambda_values = ce_systems['lambda_CE'].dropna()

# Print statistics
print(f"CE events: {len(ce_systems)}")
print(f"Mean lambda: {lambda_values.mean():.3f}")
print(f"Survival rate: {ce_systems['survived_CE'].mean():.1%}")
```

### CSV Export

Results are automatically exported to CSV by `final_analysis.py`. To export manually:

```python
df = pd.read_hdf('results.h5', 'results')
df.to_csv('results.csv', index=False)
```

## Debugging

If you encounter issues, use the interactive notebook to test individual components:

```bash
jupyter notebook Analysis.ipynb
```

The notebook allows you to:
- Test single binary evolution
- Inspect POSYDON history structure
- Debug parameter settings
- Visualize results interactively

## Performance Tips

- **First run**: Slow (~5 min) - POSYDON loads all grids
- **Subsequent runs**: Fast (~3 min per 200 systems)
- **Parallelization**: Not yet implemented, but can use multiple terminals for different metallicities
- **Memory**: ~2-4 GB per run
- **Disk**: ~10-50 MB per 200 systems (HDF5 files)

## Common Issues

### Script Hangs on "Loading steps..."
This is normal! First time loads all POSYDON grids (~2-5 minutes). Be patient.

### "Grid matching failed"
Some systems don't match interpolation grids after disruption. This is expected, the script continues.

### "Evolution not yet supported"
Certain evolutionary paths aren't in POSYDON yet. Script records error and continues.

### Out of Memory
Reduce `--n_systems` or run in batches:
```bash
python run_population.py --n_systems 100 --output batch1.h5
python run_population.py --n_systems 100 --output batch2.h5
```

Then combine results in analysis.

## Next Steps

After running your population synthesis:

1. **Analyze results**: `python final_analysis.py`
2. **View figures**: Check `results/` directory
3. **Read findings**: See `README.md` Results section
4. **Write paper**: Use figures and `summary_statistics.csv`
