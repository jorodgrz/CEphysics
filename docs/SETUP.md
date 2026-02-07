# Setup Guide

Complete installation and configuration guide for the CE Metallicity Study.

## Prerequisites

- Conda package manager
- ~50 GB disk space for POSYDON grids
- Python 3.11 or compatible version

## Installation

### 1. Create Conda Environment

```bash
conda create -n posydon python=3.11 -y
conda activate posydon
```

### 2. Install POSYDON

Clone and install from source:

```bash
cd ~/CEphysics
git clone https://github.com/POSYDON-code/POSYDON.git
cd POSYDON
pip install -e .
```

### 3. Download POSYDON Data

Download the solar metallicity grids (required):

```bash
get-posydon-data DR2_1Zsun
```

This downloads ~10 GB of stellar evolution grids. For additional metallicities:

```bash
get-posydon-data DR2_0.1Zsun   # Low metallicity (Z=0.001)
get-posydon-data DR2_0.45Zsun  # Mid metallicity (Z=0.006)
```

### 4. Set Environment Variables

Add to your `.bashrc` or `.zshrc`:

```bash
export PATH_TO_POSYDON=~/CEphysics/POSYDON
export PATH_TO_POSYDON_DATA=~/CEphysics/grids/POSYDON_data
```

Then reload:
```bash
source ~/.bashrc  # or source ~/.zshrc
```

### 5. Verify Installation

```bash
conda activate posydon
python -c "import posydon; print('POSYDON version:', posydon.__version__)"
```

Should output the POSYDON version number.

## HPC Setup (UCSD JupyterHub)

If using a shared HPC environment:

### 1. Initialize Conda
```bash
source /opt/conda/etc/profile.d/conda.sh
```

### 2. Create Environment
```bash
conda create -n posydon python=3.11 -y
conda activate posydon
```

### 3. Install POSYDON
```bash
cd ~/CEphysics/POSYDON
pip install -e .
```

### 4. Install Jupyter Kernel
```bash
conda install -y ipykernel
python -m ipykernel install --user --name posydon --display-name "Python 3.11 (posydon)"
```

### 5. Set Environment Variables
```bash
export PATH_TO_POSYDON=~/CEphysics/POSYDON
export PATH_TO_POSYDON_DATA=~/CEphysics/grids/POSYDON_data
```

## Troubleshooting

### Environment Not Found
```bash
# List available environments
conda info --envs

# Recreate if missing
conda create -n posydon python=3.11 -y
```

### Module Not Found
```bash
# Make sure environment is activated
conda activate posydon

# Reinstall POSYDON
cd ~/CEphysics/POSYDON
pip install -e .
```

### Path Not Found
```bash
# Check environment variables
echo $PATH_TO_POSYDON
echo $PATH_TO_POSYDON_DATA

# Reset if needed
export PATH_TO_POSYDON=~/CEphysics/POSYDON
export PATH_TO_POSYDON_DATA=~/CEphysics/grids/POSYDON_data
```

### Jupyter Kernel Issues
```bash
# List kernels
jupyter kernelspec list

# Remove old kernel
jupyter kernelspec remove posydon

# Reinstall
conda activate posydon
python -m ipykernel install --user --name posydon --display-name "Python 3.11 (posydon)"
```

## Documentation

- **POSYDON Official**: https://posydon.org/POSYDON/latest/
- **POSYDON Paper**: [Fragos et al. (2023)](https://ui.adsabs.harvard.edu/abs/2023ApJS..264...45F/)
- **GitHub**: https://github.com/POSYDON-code/POSYDON
