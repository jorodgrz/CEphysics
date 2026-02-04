# CE Research Project Checklist

## Setup Phase ✅

- [x] Install POSYDON v2.2.4
- [x] Create conda environment
- [x] Download POSYDON data grids (in progress)
- [x] Create project structure
- [x] Write Jupyter notebook
- [x] Write batch processing scripts
- [x] Document installation process

## Testing Phase ⏸

- [ ] Test POSYDON import and basic functions
- [ ] Evolve single binary at solar metallicity
  - [ ] M1=12 M☉, M2=10 M☉, P=500 days
  - [ ] Check for CE event
  - [ ] Extract lambda value
- [ ] Verify data extraction pipeline
- [ ] Test with 10 random binaries
- [ ] Debug any issues
- [ ] Confirm output format is correct

## Small Production Run ⏸

- [ ] Run 100 binaries at Z=0.014 (solar)
- [ ] Analyze results
- [ ] Check statistics:
  - [ ] Number of CE events
  - [ ] Survival fraction
  - [ ] Lambda distribution
- [ ] Generate test plots
- [ ] Verify results are physically reasonable

## Full Production Runs ⏸

### Z = 0.0001 (Early Universe)
- [ ] Configure parameters
- [ ] Run population synthesis
- [ ] Save results to `results_Z0.0001.h5`
- [ ] Verify completion
- [ ] Quick analysis check

### Z = 0.001 (Low metallicity)
- [ ] Configure parameters
- [ ] Run population synthesis
- [ ] Save results to `results_Z0.001.h5`
- [ ] Verify completion
- [ ] Quick analysis check

### Z = 0.006 (Sub-solar)
- [ ] Configure parameters
- [ ] Run population synthesis
- [ ] Save results to `results_Z0.006.h5`
- [ ] Verify completion
- [ ] Quick analysis check

### Z = 0.014 (Solar)
- [ ] Configure parameters
- [ ] Run population synthesis
- [ ] Save results to `results_Z0.014.h5`
- [ ] Verify completion
- [ ] Quick analysis check

## Data Analysis ⏸

### Lambda Analysis
- [ ] Plot lambda distributions for each Z
- [ ] Compare to fixed λ=0.1 and λ=0.5
- [ ] Statistical tests (KS test, etc.)
- [ ] Identify outliers

### Survival Analysis
- [ ] Calculate survival fractions vs (M1, M2, P, Z)
- [ ] Create survival probability maps
- [ ] Compare POSYDON to fixed-lambda predictions
- [ ] Quantify differences

### Metallicity Effects
- [ ] Plot survival rate vs Z
- [ ] Plot mean lambda vs Z
- [ ] Test "death trap" hypothesis
- [ ] Identify Z-dependent trends

### Energy Budget
- [ ] Extract E_rec data if available
- [ ] Analyze contribution to binding energy
- [ ] Correlate with survival outcomes
- [ ] Identify systems where E_rec is critical

### Donor State Analysis
- [ ] Separate RSG vs YSG donors
- [ ] Compare lambda distributions
- [ ] Compare survival rates
- [ ] Identify systematic differences

## Figures for Publication ⏸

- [ ] Figure 1: Parameter space coverage
- [ ] Figure 2: Lambda distributions (all Z)
- [ ] Figure 3: Survival fraction vs metallicity
- [ ] Figure 4: Survival maps in (M1, M2, P) space
- [ ] Figure 5: Comparison to fixed-lambda models
- [ ] Figure 6: Energy budget breakdown
- [ ] Figure 7: Donor state dependence
- [ ] All figures at publication quality (300 dpi)

## Writing ⏸

### Manuscript Sections
- [ ] Abstract (250 words)
- [ ] Introduction
  - [ ] Motivation
  - [ ] CE physics background
  - [ ] POSYDON overview
  - [ ] Research questions
- [ ] Methods
  - [ ] Initial population
  - [ ] POSYDON setup
  - [ ] CE identification
  - [ ] Analysis approach
- [ ] Results
  - [ ] Lambda distributions
  - [ ] Survival rates
  - [ ] Metallicity effects
  - [ ] Energy sources
- [ ] Discussion
  - [ ] Implications for DNS formation
  - [ ] Comparison to literature
  - [ ] Limitations
  - [ ] Future work
- [ ] Conclusions
- [ ] Acknowledgments
- [ ] References

### Supplementary Materials
- [ ] Full data tables
- [ ] Additional figures
- [ ] Code repository link

## Review & Submission ⏸

- [ ] Internal review by advisor
- [ ] Revisions from feedback
- [ ] Submit to arXiv
- [ ] Submit to journal (ApJ or MNRAS)
- [ ] Address referee comments
- [ ] Resubmit if needed
- [ ] Acceptance! 🎉

## Presentations ⏸

- [ ] Create talk slides
- [ ] Practice presentation
- [ ] Give group seminar
- [ ] Submit AAS abstract
- [ ] Present at conference
- [ ] Update project website

## Data Release ⏸

- [ ] Archive results on Zenodo
- [ ] Get DOI
- [ ] Upload code to GitHub
- [ ] Write documentation
- [ ] Link in paper

---

## Current Status

**Phase:** Setup Complete ✅  
**Next Task:** Wait for data grids to finish downloading, then begin Testing Phase  
**Last Updated:** January 27, 2026

## Notes

- Data grids are currently downloading
- Once complete, start with single binary evolution test
- Use `CE_research_project.ipynb` for initial exploration
- Document any issues or unexpected results
