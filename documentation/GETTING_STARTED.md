# Getting Started with Your CE Research Project

## ✅ Setup Complete!

Your POSYDON environment is properly configured with:
- POSYDON v2.2.4 installed
- Solar metallicity (Z=0.014) grids extracted
- Project scripts and notebooks ready
- Test scripts created

## 📍 Current Status

The grids are set up at: `/Users/josephrodriguez/CEphysics/CEphysics/grids/POSYDON_data/`

**Note:** When you first run POSYDON evolution, it may download additional data files (~450 MB). This is normal and only happens once.

## 🚀 Quick Start Options

### Option 1: Interactive Jupyter Notebook (Recommended)

```bash
# Activate POSYDON environment
conda activate posydon

# Navigate to project directory
cd /Users/josephrodriguez/CEphysics/CEphysics

# Launch Jupyter
jupyter notebook CE_research_project.ipynb
```

The notebook contains:
- Complete project walkthrough
- Parameter space visualization  
- Population synthesis workflow
- Analysis functions
- Step-by-step documentation

### Option 2: Test Single Binary Evolution

```bash
conda activate posydon
cd /Users/josephrodriguez/CEphysics/CEphysics
python test_single_binary.py
```

This will evolve a single 12+10 M☉ binary at solar metallicity and show:
- Whether CE occurred
- Lambda (λ) value from POSYDON grids
- Final binary state
- Evolution history

**Note:** First run may take 5-10 minutes as POSYDON downloads additional data files.

### Option 3: Small Population Test

```bash
conda activate posydon
cd /Users/josephrodriguez/CEphysics/CEphysics
python run_population.py --n_systems 5 --output test_5binaries.h5
```

This runs a test with 5 random binaries to verify the full pipeline works.

## 📊 Your Research Workflow

### Phase 1: Testing (Do This First!)

1. **Run setup test**:
   ```bash
   python test_posydon_setup.py
   ```
   Should show "✅ ALL TESTS PASSED!"

2. **Test single binary** (takes ~5-10 min first time):
   ```bash
   python test_single_binary.py
   ```

3. **Test small population** (takes ~30-60 min):
   ```bash
   python run_population.py --n_systems 10 --metallicity 0.014 --output test.h5
   ```

4. **Analyze test results**:
   ```bash
   python analyze_results.py --input test.h5 --output-dir test_analysis/
   ```

### Phase 2: Production Runs

Once testing works, run the full population for each metallicity:

```bash
# Solar metallicity (Z = 0.014)
python run_population.py \
    --metallicity 0.014 \
    --M1_samples 25 --M2_samples 25 --P_samples 30 \
    --output results_Z0.014.h5

# Can also run multiple Z values in one command:
python run_population.py \
    --metallicity 0.0001 0.001 0.006 0.014 \
    --M1_samples 20 --M2_samples 20 --P_samples 25 \
    --output results_all_Z.h5
```

**Note:** Full production runs may take hours to days depending on grid size.

### Phase 3: Analysis

```bash
# Analyze results for each metallicity
python analyze_results.py \
    --input results_Z0.014.h5 \
    --output-dir analysis_Z0.014/

# This creates:
# - lambda_distribution.png
# - metallicity_effects.png
# - parameter_space.png
# - overall_summary.csv
# - summary_by_metallicity.csv
```

## 📁 Project Files

| File | Purpose |
|------|---------|
| `CE_research_project.ipynb` | Main research notebook (interactive) |
| `run_population.py` | Batch processing script |
| `analyze_results.py` | Results analysis script |
| `test_posydon_setup.py` | Verify POSYDON is configured |
| `test_single_binary.py` | Test evolving one binary |
| `.env` | Environment variables |
| `README.md` | Project overview |

## 🎯 Research Questions

Your project investigates three key problems:

1. **Survival Problem**: Do binaries with grid-based λ survive CE more than fixed-λ models predict?

2. **Metallicity Problem**: Does low Z make CE harder (potential "death trap")?

3. **Energy Sources Problem**: Is recombination energy critical for survival?

## 💡 Tips & Troubleshooting

### If you get "PATH_TO_POSYDON not defined" error:

The test scripts set this automatically, but if you're using the Jupyter notebook, add this cell at the top:

```python
import os
from pathlib import Path

# Set POSYDON paths
project_dir = Path.cwd()
os.environ['PATH_TO_POSYDON'] = str(project_dir / "POSYDON")
os.environ['PATH_TO_POSYDON_DATA'] = str(project_dir / "grids" / "POSYDON_data")
```

### If downloads are slow:

The first time you run POSYDON evolution, it downloads ~450 MB of additional model data. This is normal. Subsequent runs won't need to download again.

### If you need additional metallicities:

You currently have solar metallicity (Z=0.014) grids. To download other metallicities:

```bash
conda activate posydon
get-posydon-data --metallicity 0.001  # Example for Z=0.001
```

Check available data at: https://posydon.org

### For faster runs on HPC:

If you have access to an HPC cluster, you can modify `run_population.py` to use MPI:

```bash
# Install MPI support
conda activate posydon
pip install mpi4py

# Run with MPI
mpirun -n 16 python run_population.py --metallicity 0.014 --output results.h5
```

## 📚 Documentation

- **POSYDON Official Docs**: https://posydon.org/POSYDON/latest/
- **POSYDON Paper**: [Fragos et al. (2023)](https://ui.adsabs.harvard.edu/abs/2023ApJS..264...45F/)
- **Tutorials**: `/POSYDON/docs/_source/tutorials-examples/`

## 🎓 Expected Outputs

From your research, you should be able to produce:

1. **Lambda distributions** by metallicity and donor type (RSG/YSG)
2. **Survival rate functions** f(M1, M2, P, Z)
3. **Comparison plots** showing POSYDON vs fixed-λ predictions
4. **Metallicity trends** in CE survival
5. **Energy budget analysis** (if E_rec data available)

These will form the basis of your research paper!

## ⚡ Performance Estimates

| Task | Time Estimate |
|------|--------------|
| Single binary | 5-10 minutes (first run), 1-2 min (subsequent) |
| 10 binaries | 30-60 minutes |
| 100 binaries | 5-10 hours |
| Full grid (~18,750 binaries/Z) | 2-7 days per Z |

Times vary based on:
- System complexity (mass transfer, CE events, etc.)
- Your computer specs
- Whether using HPC/parallelization

## 🆘 Getting Help

If you encounter issues:

1. Check that `test_posydon_setup.py` passes all tests
2. Try a single binary first (`test_single_binary.py`)
3. Check POSYDON documentation: https://posydon.org
4. Look at example notebooks in `POSYDON/docs/_source/tutorials-examples/`
5. Check POSYDON GitHub issues: https://github.com/POSYDON-code/POSYDON/issues

## 🎉 Ready to Start!

You're all set! Begin with:

```bash
conda activate posydon
jupyter notebook CE_research_project.ipynb
```

Good luck with your research! 🌟
