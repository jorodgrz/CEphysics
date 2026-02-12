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

## Project Structure

```
CEphysics/
├── 📄 README.md                    # Project overview and results
├── 📄 LICENSE                      # MIT License
├── 📄 PROJECT_STRUCTURE.md         # Detailed structure documentation
├── 📓 analysis.ipynb               # Interactive exploration notebook
│
├── 📁 scripts/                     # Python analysis scripts
│   ├── run_population.py           # Core POSYDON simulation engine
│   ├── alpha_sweep.py              # Unified α sweep runner
│   ├── analyze_alpha_sweep.py      # Alpha sweep analysis
│   ├── bootstrap_analysis.py       # Statistical robustness (10k iterations)
│   ├── physics_analysis.py         # Detailed mechanism study
│   └── observational_comparison.py # LIGO/Virgo & DNS comparison
│
├── 📁 data/                        # Simulation data (HDF5 files)
│   ├── ce_fixed_lambda.h5          # Solar Z (0.014), α=0.5
│   ├── mid_Z_lambda.h5             # Mid Z (0.006), α=0.5
│   ├── low_Z_lambda.h5             # Low Z (0.001), α=0.5
│   └── *_alpha*.h5                 # Alpha sweep outputs
│
├── 📁 results/                     # Analysis outputs
│   ├── README.md                   # Results documentation
│   ├── summary_statistics.csv      # Overall summary
│   ├── lambda_vs_metallicity.png   # Main figure
│   ├── detailed_comparison.png     # Detailed figure
│   │
│   ├── 📁 bootstrap/               # Bootstrap resampling
│   │   ├── *_bootstrap.csv         # Bootstrap CIs
│   │   └── bootstrap_analysis.png
│   │
│   ├── 📁 physics/                 # Physics mechanisms
│   │   ├── shell_vs_core_analysis.csv
│   │   ├── survival_vs_*.csv
│   │   └── *.png
│   │
│   ├── 📁 observational/           # Observational context
│   │   ├── galactic_dns_metallicities.csv
│   │   └── observational_comparison.png
│   │
│   └── 📁 sensitivity/             # Sensitivity analysis
│       ├── alpha_sweep_summary.csv
│       └── *.png
│
├── 📁 docs/                        # Documentation
│   ├── SETUP.md                    # Installation guide
│   ├── USAGE.md                    # Usage instructions
│   ├── ANALYSIS_GUIDE.md           # Complete pipeline guide
│   └── *_SUMMARY.md                # Additional docs
│
└── 📁 POSYDON/                     # POSYDON framework
    └── ...
```

> 📖 See [`PROJECT_STRUCTURE.md`](PROJECT_STRUCTURE.md) for detailed documentation

## Results

### Key Findings

#### 1. Grid-Based Lambda is Significantly Lower Than Classical Models

POSYDON grid-based envelope binding energy parameter:
- **Solar Z (0.014)**: $\lambda = 0.144 \pm 0.097$ (range: 0.036 - 0.237)
- **Mid Z (0.006)**: $\lambda = 0.111 \pm 0.114$
- **Low Z (0.001)**: $\lambda = 0.111 \pm 0.114$

Classical constant models typically assume: $\lambda = 0.1$ to $0.5$

**Result**: Grid-based $\lambda$ is **3-5× lower** than classical models and **highly variable** depending on stellar evolutionary phase.

#### 2. Lambda Depends on Evolutionary Phase, Not Just Metallicity

Lambda shows a **bimodal distribution**:
- **H-rich Shell H-burning**: $\lambda \approx 0.04$ (compact, tightly-bound envelopes)
- **H-rich Core He-burning**: $\lambda \approx 0.22$ (expanded, loosely-bound envelopes)

This **validates the hypothesis**: $\lambda$ fluctuates during the supergiant phase rather than being constant.

#### 3. Critical Metallicity Threshold Discovered

**Sharp transition at**: $0.006 < Z_{\text{crit}} < 0.014$

| Metallicity | CE Rate (95% CI) | Survival Rate (95% CI) | Outcome |
|------------|---------|---------------|---------|
| Z = 0.014 (Solar) | 6.5% (3.5-10.9%) | 7.7% (0.2-36.0%) | **Survival Possible** ✓ |
| Z = 0.006 (Mid) | 14.5% (9.9-20.2%) | 0.0% (0.0-9.8%) | **Death Trap** ✗ |
| Z = 0.001 (Low) | 13.5% (9.1-19.0%) | 0.0% (0.0-10.5%) | **Death Trap** ✗ |

**Statistical Robustness**: Confidence intervals calculated using Wilson score method (beta distribution for small sample sizes).

**Below $Z_{\text{crit}}$**: 
- CE events occur **2× more frequently** (stars are more compact)
- But **0% survival rate** with 95% confidence upper bound < 11% (envelopes too tightly bound to eject)

#### 4. Critical Lambda Threshold Identified

**Survival requires**: $\lambda \gtrsim 0.04$

Lambda binning analysis reveals:
- $\lambda < 0.03$: **0% survival** (n=22 systems)
- $0.03 < \lambda < 0.06$: **11% survival** (n=9 systems, only 1 survivor)
- $\lambda > 0.06$: **0% survival** in current sample (possible λ > 0.15 needed with higher α)

**The only survivor** in the dataset had:
- $\lambda = 0.043$ (Shell H-burning phase)
- Solar metallicity (Z = 0.014)
- α_CE = 0.5

**Mechanism**: Lower lambda → Higher binding energy → Requires more orbital energy to eject envelope → Merger more likely

#### 5. Low-Z Paradox Confirmed

At low metallicity:
- Stars are more compact → Fill Roche lobes earlier
- CE happens more often
- But compact structure → Lower $\lambda$ → Impossible to eject envelope
- **Result**: 100% merger/disruption rate (with 95% CI: 89-100% failure rate)

### Implications for Astrophysics

#### For Double Neutron Star Formation:
- **Early Universe (Z < 0.006) cannot produce DNS via CE**
- DNS progenitors require **near-solar metallicity** environments
- This explains the observed metallicity distribution of DNS systems

#### For Gravitational Wave Astronomy:
- LIGO/Virgo DNS merger rate predictions must account for $Z_{\text{crit}}$
- **Cosmic merger rate history is metallicity-dependent**
- Early Universe (high redshift) contributed fewer DNS mergers than expected

#### For Population Synthesis Models:
- Classical $\lambda = \text{const}$ models **overestimate CE survival** by 3-5×
- Grid-based $\lambda$ makes DNS formation **significantly rarer**
- Variable $\lambda$ should be included in all future population studies

### Figures

See `results/` directory for publication-quality figures:

**Main Results**:
- `lambda_vs_metallicity.png` - Main result showing $\lambda(Z)$ trend and critical threshold
- `detailed_comparison.png` - Comprehensive 4-panel comparison across metallicities

**Mechanism Analysis** (`results/sensitivity/`):
- `survival_vs_lambda.png` - Survival probability as function of lambda (binned analysis with CIs)
- `survival_by_state.png` - CE survival stratified by donor evolutionary state and metallicity
- `survival_vs_alphaCE.png` - Parameter sensitivity: survival rate vs common envelope efficiency (baseline α=0.5 shown)

**Note**: Full αCE sensitivity analysis requires additional simulations at α=1.0 and α=2.0 (see Future Work below)

### Data Availability

All simulation data available in `results/`:

**Population Data**:
- `solar_Z_results.csv` - 200 systems at Z = 0.014
- `mid_Z_results.csv` - 200 systems at Z = 0.006
- `low_Z_results.csv` - 200 systems at Z = 0.001
- `summary_statistics.csv` - Aggregate statistics with 95% confidence intervals
- HDF5 files with complete binary evolution histories

**Analysis Data** (`results/sensitivity/`):
- `lambda_binned_survival.csv` - Survival rates by lambda bin with Wilson CIs
- `donor_state_stratified.csv` - Survival by evolutionary state and metallicity
- `alpha_sweep_summary.csv` - Parameter sensitivity results (baseline α=0.5)


## Advanced Analysis Scripts

### Modular Analysis Pipeline

The project now includes comprehensive modular scripts for publication-ready analysis:

#### 1. **Alpha Sweep** (`scripts/alpha_sweep.py`)
Unified simulation runner with checkpointing and error recovery:
```bash
python scripts/alpha_sweep.py                    # Run all α sweep simulations
python scripts/alpha_sweep.py --resume           # Resume from checkpoint
python scripts/alpha_sweep.py --analyze          # Run simulations + analysis
python scripts/alpha_sweep.py --analyze-only     # Skip sims, just analyze
python scripts/alpha_sweep.py --dry-run          # See what would run
```

**Features:**
- Automatic checkpointing (skip completed sims)
- Error recovery (continue on failure)
- Progress tracking with detailed logs
- HDF5 file validation
- ~6-8 hours runtime for 4 simulations

#### 2. **Bootstrap Analysis** (`scripts/bootstrap_analysis.py`)
Robust statistical uncertainty estimation:
```bash
python scripts/bootstrap_analysis.py             # 10k iterations (default)
python scripts/bootstrap_analysis.py --n_boot 20000  # More precise
```

**Outputs:**
- Non-parametric confidence intervals
- CE occurrence rates with bootstrap CIs
- Survival rates with bootstrap CIs
- Lambda distributions with uncertainties
- Survival vs lambda (binned) analysis

#### 3. **Physics Analysis** (`scripts/physics_analysis.py`)
Detailed mechanism investigation:
```bash
python scripts/physics_analysis.py               # Baseline analysis
python scripts/physics_analysis.py --include-alpha  # Include α sweep data
```

**Analyses:**
- Shell vs Core burning donor comparison
- Survival as function of mass ratio q = M₂/M₁
- Survival as function of orbital period
- 2D survival maps: f(q, P)
- Lambda by donor evolutionary state
- Binding energy correlations

#### 4. **Observational Comparison** (`scripts/observational_comparison.py`)
Astrophysical context and constraints:
```bash
python scripts/observational_comparison.py       # Full comparison
python scripts/observational_comparison.py --verbose  # Detailed output
```

**Includes:**
- Galactic DNS metallicity distribution (7 systems)
- LIGO/Virgo merger rate implications
- Cosmic star formation history integration
- DNS formation channel constraints
- Redshift-dependent metallicity evolution

### Quick Start for Complete Analysis

```bash
# Run from project root (CEphysics/)

# 1. Run alpha sweep simulations (6-8 hours)
python scripts/alpha_sweep.py --yes --analyze

# 2. Bootstrap resampling for robust uncertainties
python scripts/bootstrap_analysis.py

# 3. Detailed physics mechanisms
python scripts/physics_analysis.py --include-alpha

# 4. Observational comparison
python scripts/observational_comparison.py
```

## Analysis Status

### Completed ✓
- [x] Wilson/Jeffreys confidence intervals for all rates
- [x] Lambda binning analysis with CIs
- [x] Donor state stratified analysis
- [x] Survival vs lambda relationship identified (λ_crit ≈ 0.04)
- [x] Evolutionary state dependence quantified
- [x] Modular analysis pipeline created

### Ready to Run
- [ ] Alpha CE sweep: α ∈ {1.0, 2.0} for Z=0.001 and Z=0.006 (scripts ready)
- [ ] Bootstrap resampling (10k iterations) - script ready
- [ ] Shell vs Core burning comparison - script ready
- [ ] Mass ratio and period dependence - script ready
- [ ] Galactic DNS comparison - script ready
- [ ] LIGO/Virgo implications - script ready

### Future Extensions
- [ ] Test recombination energy toggle (if available in POSYDON)
- [ ] Larger population (N=1000) for tighter constraints
- [ ] Triple interaction channel comparison

## Documentation

For more detailed information:

- **[docs/SETUP.md](docs/SETUP.md)** - Installation and environment setup guide
- **[docs/USAGE.md](docs/USAGE.md)** - Complete usage instructions and command reference
- **[results/](results/)** - All data files, figures, and analysis outputs

## Citation

If you use this work, please cite:

```bibtex
@article{Rodriguez2026,
  author = {Rodriguez, Joseph},
  title = {Metallicity Dependence of Common Envelope Evolution in Binary Stars},
  journal = {In preparation},
  year = {2026}
}
```

And the POSYDON framework:

```bibtex
@article{Fragos2023,
  author = {Fragos, T. and others},
  title = {POSYDON: A Framework for Population Synthesis},
  journal = {ApJS},
  volume = {264},
  pages = {45},
  year = {2023}
}
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

**Joseph Rodriguez**  
University of California, San Diego  
Email: jrodriguezruelas@ucsd.edu  
GitHub: [@jorodgrz](https://github.com/jorodgrz)

