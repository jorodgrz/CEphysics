# POSYDON Installation Guide

## Installation Complete! ✓

POSYDON version 2.2.4 has been successfully installed in your conda environment.

## Environment Setup

### Conda Environment
- **Environment name**: `posydon`
- **Python version**: 3.11.14
- **POSYDON version**: 2.2.4

### Activating the Environment

To use POSYDON, you need to activate the conda environment:

```bash
conda activate posydon
```

### Verifying Installation

Test that POSYDON is properly installed:

```bash
python -c "import posydon; print('POSYDON version:', posydon.__version__)"
```

## POSYDON Data

POSYDON requires data grids to run simulations. The data is stored separately and can be downloaded using:

```bash
# After activating the posydon environment
get-posydon-data
```

This will download the necessary MESA grids and other data files needed for population synthesis calculations.

## Available Commands

Once the environment is activated, you'll have access to these POSYDON commands:

- `posydon-popsyn` - Run population synthesis
- `posydon-run-grid` - Run MESA grids
- `posydon-setup-grid` - Setup grid parameters
- `posydon-run-pipeline` - Run processing pipeline
- `posydon-setup-pipeline` - Setup pipeline parameters
- `get-posydon-data` - Download POSYDON data

## Quick Start

1. Activate the environment:
   ```bash
   conda activate posydon
   ```

2. Download the data (if not already done):
   ```bash
   get-posydon-data
   ```

3. Start exploring! Check the [POSYDON documentation](https://posydon.org/POSYDON/latest/index.html) for tutorials.

## Installed Dependencies

The following key packages were installed with POSYDON:
- numpy 1.26.4
- scipy 1.14.1
- astropy 6.1.6
- pandas 2.2.3
- scikit-learn 1.2.2
- matplotlib 3.9.2
- h5py 3.12.1
- tables 3.10.1

## Troubleshooting

If you encounter any issues:

1. Make sure the conda environment is activated:
   ```bash
   conda activate posydon
   ```

2. Check your Python version:
   ```bash
   python --version  # Should be 3.11.x
   ```

3. Verify POSYDON installation:
   ```bash
   pip show posydon
   ```

## Documentation

- Official documentation: https://posydon.org/POSYDON/latest/index.html
- GitHub repository: https://github.com/POSYDON-code/POSYDON
- Paper: [Fragos et al. (2023)](https://ui.adsabs.harvard.edu/abs/2023ApJS..264...45F/abstract)

## Deactivating the Environment

When you're done working with POSYDON:

```bash
conda deactivate
```
