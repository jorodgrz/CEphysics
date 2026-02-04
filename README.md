# CEphysics: Common Envelope Evolution in Binary Star Systems

> A POSYDON-based study of Common Envelope evolution in Double Neutron Star progenitors

## Research Question

How do grid-based binding energies in POSYDON affect the efficiency parameter $\alpha_{\text{CE}}$ of the first Common Envelope (CE) phase in Double Neutron Star (DNS) progenitors across different metallicities ($Z$)?

## Breakdown

### 1. The "Survival" Problem
Many systems that "should" merge according to old models might survive in POSYDON because the binding energy ($E_{\text{bind}}$) calculated from the MESA grids is lower (making the envelope easier to eject with a given $\alpha_{\text{CE}}$).

### 2. The "Metallicity" Problem
Stars at low metallicity (early Universe) are more compact. Does this make $\lambda$ so low that Common Envelope evolution becomes a "death trap" for black hole progenitors at low $Z$?

### 3. The "Energy Sources" Problem
By looking at POSYDON's data, you can see if including recombination energy ($E_{\text{rec}}$, stored in ionized atoms) is the difference between a binary merging and it becoming a Gravitational Wave (GW) source.

## Methodology

### 1. The Initial Population

Generate a grid of binaries with:
- Primary Mass ($M_1$): $8 - 20 \, M_{\odot}$
- Secondary Mass ($M_2$): $8 - 20 \, M_{\odot}$
- Orbital Period ($P_{\text{orb}}$): $100 - 5000$ days (wide enough to allow the primary to become a giant before interacting)

### 2. The Variables to Track

When you extract the data, you want to create a table of all systems that reached the StepCEE (Common Envelope Event). You will look for:
- **S1_lambda** ($\lambda_{\text{env}}$): The binding energy parameter of the primary's envelope
- **S1_state**: Was it a Red Supergiant (RSG) or a Yellow Supergiant (YSG)?
- **Result**: Did it survive (binary) or merge (single star)?

### 3. The Comparison (The "Science" part)

Compare your POSYDON results to a "Fixed $\lambda$" model:
- **The Baseline**: Assume $\lambda = 0.1$ or $0.5$ (common in older papers)
- **The POSYDON reality**: Use the values interpolated from the MESA grids

**Hypothesis to test**: "I expect POSYDON to show that stars with convective envelopes have a variable $\lambda_{\text{env}}$ that fluctuates during the supergiant phase, allowing for a wider range of DNS survivors than predicted by static $\lambda = \text{const}$ models."

## Project Files

- **CE_research_project.ipynb** - Main Jupyter notebook for interactive analysis
- **run_population.py** - Python script for batch processing population synthesis  
- **analyze_results.py** - Results analysis and plotting script
- **test_posydon_setup.py** - Verify POSYDON installation
- **test_single_binary.py** - Test single binary evolution
- **GETTING_STARTED.md** - Complete quick-start guide
- **documentation/INSTALLATION.md** - POSYDON installation guide

## Quick Start

### 1. Activate POSYDON Environment

```bash
conda activate posydon
```

### 2. Launch Jupyter Notebook

```bash
jupyter notebook CE_research_project.ipynb
```

### 3. Or Run Batch Processing

```bash
# Test run with small sample
python run_population.py --n_systems 10 --output test_results.h5

# Full run for single metallicity
python run_population.py --metallicity 0.014 --output solar_Z_results.h5

# Multiple metallicities
python run_population.py --metallicity 0.0001 0.001 0.006 0.014 --output all_Z_results.h5
```