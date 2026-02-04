# Common Envelope Evolution Research Project

**Principal Investigator:** Joseph Rodriguez  
**Institution:** [Your Institution]  
**Date Started:** January 27, 2026  
**POSYDON Version:** 2.2.4

---

## Research Objective

Investigate how grid-based binding energies in POSYDON affect the efficiency parameter $\alpha_{\text{CE}}$ of the first Common Envelope (CE) phase in Double Neutron Star (DNS) progenitors across different metallicities.

## Scientific Motivation

Traditional binary evolution models use fixed values for the envelope binding energy parameter $\lambda$ (typically 0.1 or 0.5). POSYDON interpolates $\lambda$ from detailed MESA stellar structure grids, allowing it to vary based on the star's evolutionary state, mass, and metallicity. This could fundamentally change our understanding of which binaries survive CE and contribute to the DNS population.

## Three Key Problems

### 1. The "Survival" Problem
**Question:** Do systems that "should" merge according to old fixed-$\lambda$ models actually survive in POSYDON?

**Why it matters:** If POSYDON's grid-based $E_{\text{bind}}$ is systematically lower than assumed in classical models, more binaries will survive CE, potentially increasing DNS merger rates observed by LIGO/Virgo.

### 2. The "Metallicity" Problem  
**Question:** Does low metallicity create a "death trap" for CE at low $Z$?

**Why it matters:** Early-universe stars (low $Z$) are more compact, which may decrease $\lambda$, making envelope ejection harder. This could suppress DNS formation in the early universe and affect gravitational wave event rates vs. redshift.

### 3. The "Energy Sources" Problem
**Question:** Is recombination energy ($E_{\text{rec}}$) the critical factor determining CE survival?

**Why it matters:** POSYDON can track different energy sources contributing to envelope binding. Understanding which dominates could reveal the physics controlling CE outcomes.

## Hypothesis

> "I expect POSYDON to show that stars with convective envelopes have a variable $\lambda_{\text{env}}$ that fluctuates during the supergiant phase, allowing for a wider range of DNS survivors than predicted by static $\lambda = \text{const}$ models."

---

## Methodology

### Initial Population

Generate a grid of binaries with:
- **Primary Mass** ($M_1$): $8 - 20 \, M_{\odot}$
- **Secondary Mass** ($M_2$): $8 - 20 \, M_{\odot}$
- **Orbital Period** ($P_{\text{orb}}$): $100 - 5000$ days
- **Metallicities**: $Z = [0.0001, 0.001, 0.006, 0.014]$

### Variables to Track

For each system that experiences CE, record:
1. **$\lambda_{\text{env}}$** - Binding energy parameter from POSYDON grids
2. **Donor state** - Red Supergiant (RSG) vs Yellow Supergiant (YSG)
3. **Survival outcome** - Did the binary survive or merge?
4. **Energy budget** - Contribution of $E_{\text{rec}}$ and other energy sources
5. **Final state** - DNS, NS-BH, BBH, disrupted, etc.

### Analysis Plan

Compare POSYDON results to baseline models:
- **Baseline:** Fixed $\lambda = 0.1$ and $\lambda = 0.5$
- **POSYDON:** Variable $\lambda$ from MESA grids
- **Metrics:**
  - Survival fraction vs $(M_1, M_2, P, Z)$
  - $\lambda$ distribution and correlations
  - Metallicity dependence of outcomes
  - Role of recombination energy

---

## Project Structure

```
CEphysics/
├── README.md                    # Project summary
├── PROJECT_OVERVIEW.md          # This file - detailed research plan
├── CE_research_project.ipynb    # Main Jupyter notebook (interactive)
├── run_population.py            # Batch processing script
├── analyze_results.py           # Results analysis script
├── documentation/
│   └── INSTALLATION.md          # POSYDON setup guide
├── POSYDON/                     # POSYDON source code
└── results/                     # Output directory (created during runs)
```

## Workflow

### Phase 1: Setup (✓ COMPLETE)
1. ✅ Install POSYDON v2.2.4
2. ✅ Download POSYDON data grids (in progress)
3. ✅ Create parameter space
4. ✅ Setup analysis notebooks/scripts

### Phase 2: Testing (NEXT)
1. ⏸ Evolve single test binary
2. ⏸ Verify CE detection and data extraction
3. ⏸ Run small population (~10-100 binaries)
4. ⏸ Debug and refine analysis pipeline

### Phase 3: Production Runs
1. ⏸ Run full grid for each metallicity
2. ⏸ Extract CE events and properties
3. ⏸ Build results database

### Phase 4: Analysis
1. ⏸ Compare grid-based vs fixed-$\lambda$ outcomes
2. ⏸ Investigate metallicity dependence
3. ⏸ Analyze energy budget contributions
4. ⏸ Create publication-quality figures

### Phase 5: Publication
1. ⏸ Write draft manuscript
2. ⏸ Internal review
3. ⏸ Submit to journal (ApJ or MNRAS)

---

## Usage Guide

### Interactive Analysis (Recommended for Exploration)

```bash
# Activate POSYDON environment
conda activate posydon

# Launch Jupyter notebook
jupyter notebook CE_research_project.ipynb
```

The notebook contains:
- Complete walkthrough of the methodology
- Interactive plots and analysis
- Step-by-step documentation
- Example code for all stages

### Batch Processing (For Production Runs)

```bash
# Test run with small sample
python run_population.py --n_systems 10 --output test.h5

# Single metallicity run
python run_population.py \
    --metallicity 0.014 \
    --M1_samples 25 --M2_samples 25 --P_samples 30 \
    --output solar_metallicity.h5

# Multiple metallicities
python run_population.py \
    --metallicity 0.0001 0.001 0.006 0.014 \
    --M1_samples 20 --M2_samples 20 --P_samples 25 \
    --output all_metallicities.h5
```

### Results Analysis

```bash
# Analyze results and generate plots
python analyze_results.py \
    --input solar_metallicity.h5 \
    --output-dir analysis_Z0.014/

# Output includes:
#   - lambda_distribution.png
#   - metallicity_effects.png
#   - parameter_space.png
#   - overall_summary.csv
#   - summary_by_metallicity.csv
```

---

## Expected Outcomes

### Scientific Deliverables

1. **Survival Rate Functions**
   - $f_{\text{survive}}(M_1, M_2, P, Z)$ for POSYDON vs fixed-$\lambda$
   - Quantify difference in DNS formation channels

2. **Lambda Distributions**
   - Empirical $p(\lambda | M, Z, \text{state})$
   - Compare to standard assumptions

3. **Metallicity Trends**
   - Test if low-$Z$ suppresses CE survival
   - Implications for high-redshift GW sources

4. **Energy Budget Analysis**
   - Relative importance of $E_{\text{rec}}$ vs other terms
   - Identify systems where recombination is critical

### Publications

**Primary Paper** (Target: ApJ or MNRAS)
- Title: "Grid-Based Binding Energies and Common Envelope Survival: Implications for Double Neutron Star Formation"
- Estimated length: 15-20 pages
- Target submission: Q2 2026

**Possible Follow-ups:**
- Metallicity dependence and GW event rates vs redshift
- Comparison with alternative CE prescriptions
- Population synthesis predictions for next-gen GW detectors

### Presentations

- AAS meeting (poster or talk)
- Compact Objects group seminar
- Possible invited talk at POSYDON collaboration meeting

---

## Data Management

### Input Data
- POSYDON grids: `~/Downloads/POSYDON_data/` (~several GB)
- Managed by POSYDON data retrieval system

### Output Data
- Population results: HDF5 format (`.h5` files)
- Analysis tables: CSV format
- Figures: PNG format (high-resolution for publication)

### Backup Strategy
- Version control: Git repository (code only)
- Data backup: External drive + cloud storage
- Results archive: Zenodo DOI after publication

---

## Timeline

| Phase | Duration | Target Completion |
|-------|----------|-------------------|
| Setup & Testing | 2 weeks | Feb 10, 2026 |
| Production Runs | 4 weeks | Mar 10, 2026 |
| Analysis | 3 weeks | Mar 31, 2026 |
| Writing | 4 weeks | Apr 30, 2026 |
| Revision & Submission | 2 weeks | May 15, 2026 |

**Note:** Timeline assumes successful POSYDON data download and no major technical issues.

---

## Computational Resources

### Requirements
- **CPU:** Population synthesis is embarrassingly parallel
  - Option 1: Local machine (days to weeks)
  - Option 2: HPC cluster (hours to days)
- **Memory:** ~2-4 GB per parallel process
- **Storage:** ~10-50 GB for full results database

### Optimization
- Use `run_population.py` with HPC job arrays
- Parallelize over metallicity bins
- Consider MPI implementation for very large grids

---

## References

### Key Papers

1. **Fragos et al. (2023)** - POSYDON methodology
   - https://ui.adsabs.harvard.edu/abs/2023ApJS..264...45F/

2. **Andrews et al. (2024)** - POSYDON implementation details
   - https://ui.adsabs.harvard.edu/abs/2024arXiv241102376A/

3. **Ivanova et al. (2013)** - CE evolution review
   - https://ui.adsabs.harvard.edu/abs/2013A%26ARv..21...59I/

4. **Vigna-Gómez et al. (2018)** - DNS formation channels
   - https://ui.adsabs.harvard.edu/abs/2018MNRAS.481.4009V/

### Software

- **POSYDON:** https://github.com/POSYDON-code/POSYDON
- **Documentation:** https://posydon.org/POSYDON/latest/

---

## Contact

**Joseph Rodriguez**  
Email: [your email]  
GitHub: [your github]  

**Supervisor/Advisor:** [if applicable]

---

## Acknowledgments

This research uses POSYDON, developed by the POSYDON collaboration led by Tassos Fragos (Université de Genève) and Vicky Kalogera (Northwestern University).

---

*Last Updated: January 27, 2026*
