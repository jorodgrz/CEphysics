#!/usr/bin/env python3
"""
Parameter sensitivity analysis: αCE sweep

This script analyzes the robustness of CE results across different
Common Envelope efficiency parameters (αCE).

Usage:
    python analyze_alpha_sweep.py

Required data files (run simulations first):
    - ce_fixed_lambda.h5 (Solar Z, α=0.5) ✓ Already exists
    - mid_Z_lambda.h5 (Mid Z, α=0.5) ✓ Already exists  
    - low_Z_lambda.h5 (Low Z, α=0.5) ✓ Already exists
    - low_Z_alpha1p0.h5 (Low Z, α=1.0) - Run needed
    - low_Z_alpha2p0.h5 (Low Z, α=2.0) - Run needed
    - mid_Z_alpha1p0.h5 (Mid Z, α=1.0) - Run needed
    - mid_Z_alpha2p0.h5 (Mid Z, α=2.0) - Run needed

To generate missing data files, run:
    python run_population.py --metallicity 0.001 --alpha_CE 1.0 --n_systems 200 --output low_Z_alpha1p0.h5
    python run_population.py --metallicity 0.001 --alpha_CE 2.0 --n_systems 200 --output low_Z_alpha2p0.h5
    python run_population.py --metallicity 0.006 --alpha_CE 1.0 --n_systems 200 --output mid_Z_alpha1p0.h5
    python run_population.py --metallicity 0.006 --alpha_CE 2.0 --n_systems 200 --output mid_Z_alpha2p0.h5
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.stats import beta
import sys

# Create output directory
results_dir = Path('results')
sensitivity_dir = results_dir / 'sensitivity'
sensitivity_dir.mkdir(parents=True, exist_ok=True)

print("="*70)
print("PARAMETER SENSITIVITY ANALYSIS - αCE SWEEP")
print("="*70)

def wilson_ci(k, n, alpha=0.05):
    """Wilson score confidence interval for binomial proportion."""
    if n == 0:
        return 0.0, 0.0
    if k == 0:
        lower = 0.0
        upper = 1 - alpha**(1/n)
    elif k == n:
        lower = alpha**(1/n)
        upper = 1.0
    else:
        lower = beta.ppf(alpha/2, k, n-k+1) if k > 0 else 0.0
        upper = beta.ppf(1-alpha/2, k+1, n-k) if k < n else 1.0
    return lower * 100, upper * 100

# Define expected data files
data_files = [
    # Solar metallicity (only α=0.5 available)
    {'file': 'data/ce_fixed_lambda.h5', 'Z': 0.014, 'Z_label': 'Solar', 'alpha': 0.5, 'required': True},
    
    # Mid metallicity
    {'file': 'data/mid_Z_lambda.h5', 'Z': 0.006, 'Z_label': 'Mid', 'alpha': 0.5, 'required': True},
    {'file': 'data/mid_Z_alpha1p0.h5', 'Z': 0.006, 'Z_label': 'Mid', 'alpha': 1.0, 'required': False},
    {'file': 'data/mid_Z_alpha2p0.h5', 'Z': 0.006, 'Z_label': 'Mid', 'alpha': 2.0, 'required': False},
    
    # Low metallicity
    {'file': 'data/low_Z_lambda.h5', 'Z': 0.001, 'Z_label': 'Low', 'alpha': 0.5, 'required': True},
    {'file': 'data/low_Z_alpha1p0.h5', 'Z': 0.001, 'Z_label': 'Low', 'alpha': 1.0, 'required': False},
    {'file': 'data/low_Z_alpha2p0.h5', 'Z': 0.001, 'Z_label': 'Low', 'alpha': 2.0, 'required': False},
]

# Load available datasets
print("\nChecking for data files...")
loaded_data = []
missing_files = []

for file_info in data_files:
    filepath = Path(file_info['file'])
    if filepath.exists():
        try:
            df = pd.read_hdf(filepath, 'results')
            loaded_data.append({
                'data': df,
                'Z': file_info['Z'],
                'Z_label': file_info['Z_label'],
                'alpha': file_info['alpha'],
                'file': file_info['file']
            })
            print(f"  ✓ {file_info['file']} (Z={file_info['Z']}, α={file_info['alpha']})")
        except Exception as e:
            print(f"  ✗ Error loading {file_info['file']}: {e}")
            if file_info['required']:
                missing_files.append(file_info['file'])
    else:
        status = "REQUIRED" if file_info['required'] else "optional"
        print(f"  - {file_info['file']} ({status})")
        if file_info['required']:
            missing_files.append(file_info['file'])

if missing_files:
    print(f"\n✗ ERROR: Required files missing: {', '.join(missing_files)}")
    sys.exit(1)

if len(loaded_data) < 3:
    print("\n⚠ WARNING: Only baseline data (α=0.5) available.")
    print("Cannot perform full αCE sensitivity analysis.")
    print("\nTo complete the analysis, run these simulations:")
    print("  python run_population.py --metallicity 0.001 --alpha_CE 1.0 --n_systems 200 --output low_Z_alpha1p0.h5")
    print("  python run_population.py --metallicity 0.001 --alpha_CE 2.0 --n_systems 200 --output low_Z_alpha2p0.h5")
    print("  python run_population.py --metallicity 0.006 --alpha_CE 1.0 --n_systems 200 --output mid_Z_alpha1p0.h5")
    print("  python run_population.py --metallicity 0.006 --alpha_CE 2.0 --n_systems 200 --output mid_Z_alpha2p0.h5")
    print("\nGenerating baseline analysis only...")

print(f"\n✓ Loaded {len(loaded_data)} datasets")

# ============================================================================
# ANALYSIS: Compute statistics for each α, Z combination
# ============================================================================
print("\n" + "="*70)
print("CALCULATING STATISTICS")
print("="*70)

sweep_results = []

for dataset in loaded_data:
    df = dataset['data']
    Z = dataset['Z']
    Z_label = dataset['Z_label']
    alpha = dataset['alpha']
    
    total = len(df)
    ce_count = (df['CE_occurred'] == True).sum()
    survival_count = df['survived_CE'].sum()
    
    ce_rate = ce_count / total * 100
    survival_rate = survival_count / ce_count * 100 if ce_count > 0 else 0
    
    # Confidence intervals
    ce_ci_low, ce_ci_high = wilson_ci(ce_count, total)
    if ce_count > 0:
        surv_ci_low, surv_ci_high = wilson_ci(survival_count, ce_count)
    else:
        surv_ci_low, surv_ci_high = 0.0, 0.0
    
    # Lambda statistics
    ce_with_lambda = df[(df['CE_occurred'] == True) & (df['lambda_CE'].notna())]
    if len(ce_with_lambda) > 0:
        lambda_mean = ce_with_lambda['lambda_CE'].mean()
        lambda_std = ce_with_lambda['lambda_CE'].std()
    else:
        lambda_mean = lambda_std = np.nan
    
    sweep_results.append({
        'Metallicity': Z_label,
        'Z': Z,
        'alpha_CE': alpha,
        'Total_Systems': total,
        'CE_Events': ce_count,
        'CE_Rate_%': ce_rate,
        'CE_Rate_CI_Low_%': ce_ci_low,
        'CE_Rate_CI_High_%': ce_ci_high,
        'Survivors': survival_count,
        'Survival_Rate_%': survival_rate,
        'Survival_CI_Low_%': surv_ci_low,
        'Survival_CI_High_%': surv_ci_high,
        'Lambda_Mean': lambda_mean,
        'Lambda_Std': lambda_std
    })
    
    print(f"\n{Z_label} Z (Z={Z}), α={alpha}:")
    print(f"  CE rate: {ce_rate:.1f}% (CI: {ce_ci_low:.1f}-{ce_ci_high:.1f}%)")
    print(f"  Survival: {survival_rate:.1f}% (CI: {surv_ci_low:.1f}-{surv_ci_high:.1f}%)")
    print(f"  Lambda: {lambda_mean:.3f} ± {lambda_std:.3f}")

# Save results
sweep_df = pd.DataFrame(sweep_results)
sweep_df.to_csv(sensitivity_dir / 'alpha_sweep_summary.csv', index=False)
print(f"\n✓ Saved: {sensitivity_dir / 'alpha_sweep_summary.csv'}")

# ============================================================================
# FIGURE: Survival Rate vs αCE
# ============================================================================
print("\n" + "="*70)
print("GENERATING FIGURES")
print("="*70)

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Plot 1: Survival rate vs alpha
ax = axes[0]

for Z_label, color, marker in [('Solar', 'orange', 'o'), ('Mid', 'blue', 's'), ('Low', 'purple', '^')]:
    Z_data = sweep_df[sweep_df['Metallicity'] == Z_label].sort_values('alpha_CE')
    
    if len(Z_data) > 0:
        ax.errorbar(Z_data['alpha_CE'], Z_data['Survival_Rate_%'], 
                    yerr=[Z_data['Survival_Rate_%'] - Z_data['Survival_CI_Low_%'],
                          Z_data['Survival_CI_High_%'] - Z_data['Survival_Rate_%']],
                    marker=marker, markersize=10, linewidth=2.5, capsize=6,
                    label=f'{Z_label} Z (Z={Z_data["Z"].values[0]})',
                    color=color, markerfacecolor=color, markeredgecolor='black', markeredgewidth=2)

ax.set_xlabel('Common Envelope Efficiency (αCE)', fontsize=14, weight='bold')
ax.set_ylabel('CE Survival Rate (%)', fontsize=14, weight='bold')
ax.set_title('Survival Rate vs αCE Parameter', fontsize=16, weight='bold')
ax.legend(fontsize=11, loc='best')
ax.grid(True, alpha=0.3, linewidth=1.5)
ax.set_xlim(0.3, max(sweep_df['alpha_CE']) + 0.3)

# Add alpha values as reference
for alpha_val in [0.5, 1.0, 2.0]:
    if alpha_val in sweep_df['alpha_CE'].values:
        ax.axvline(alpha_val, color='gray', linestyle='--', alpha=0.3, linewidth=1)

# Plot 2: CE occurrence rate vs alpha
ax = axes[1]

for Z_label, color, marker in [('Solar', 'orange', 'o'), ('Mid', 'blue', 's'), ('Low', 'purple', '^')]:
    Z_data = sweep_df[sweep_df['Metallicity'] == Z_label].sort_values('alpha_CE')
    
    if len(Z_data) > 0:
        ax.errorbar(Z_data['alpha_CE'], Z_data['CE_Rate_%'], 
                    yerr=[Z_data['CE_Rate_%'] - Z_data['CE_Rate_CI_Low_%'],
                          Z_data['CE_Rate_CI_High_%'] - Z_data['CE_Rate_%']],
                    marker=marker, markersize=10, linewidth=2.5, capsize=6,
                    label=f'{Z_label} Z (Z={Z_data["Z"].values[0]})',
                    color=color, markerfacecolor=color, markeredgecolor='black', markeredgewidth=2)

ax.set_xlabel('Common Envelope Efficiency (αCE)', fontsize=14, weight='bold')
ax.set_ylabel('CE Occurrence Rate (%)', fontsize=14, weight='bold')
ax.set_title('CE Occurrence vs αCE Parameter', fontsize=16, weight='bold')
ax.legend(fontsize=11, loc='best')
ax.grid(True, alpha=0.3, linewidth=1.5)
ax.set_xlim(0.3, max(sweep_df['alpha_CE']) + 0.3)

# Add alpha values as reference
for alpha_val in [0.5, 1.0, 2.0]:
    if alpha_val in sweep_df['alpha_CE'].values:
        ax.axvline(alpha_val, color='gray', linestyle='--', alpha=0.3, linewidth=1)

plt.tight_layout()
plt.savefig(sensitivity_dir / 'survival_vs_alphaCE.png', dpi=300, bbox_inches='tight')
print(f"\n✓ Saved: {sensitivity_dir / 'survival_vs_alphaCE.png'}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*70)
print("SENSITIVITY ANALYSIS SUMMARY")
print("="*70)

if len(loaded_data) >= 5:  # Full sweep available
    print("\n✓ Full αCE sweep completed!")
    print("\nKey findings:")
    
    # Check if low-Z death trap persists
    low_Z_data = sweep_df[sweep_df['Metallicity'] == 'Low']
    if len(low_Z_data) >= 2:
        if low_Z_data['Survival_Rate_%'].max() == 0:
            print("  1. Low-Z death trap is ROBUST across all αCE values")
            print(f"     → 0% survival for α = {', '.join(map(str, low_Z_data['alpha_CE'].values))}")
        else:
            print("  1. Low-Z survival varies with αCE")
    
    # Check lambda variation
    lambda_variation = sweep_df.groupby('Metallicity')['Lambda_Mean'].std()
    print(f"\n  2. Lambda variation across αCE:")
    for met in lambda_variation.index:
        print(f"     {met}: σ(λ) = {lambda_variation[met]:.4f}")
    
else:
    print("\n⚠ Partial analysis only (baseline α=0.5 data)")
    print("\nBaseline findings:")
    for _, row in sweep_df.iterrows():
        print(f"\n  {row['Metallicity']} Z (α={row['alpha_CE']}):")
        print(f"    Survival: {row['Survival_Rate_%']:.1f}% ± ({row['Survival_CI_Low_%']:.1f}-{row['Survival_CI_High_%']:.1f}%)")
    
    print("\n→ Run additional simulations for complete sensitivity analysis")

print("\n" + "="*70)
print("ANALYSIS COMPLETE")
print("="*70)
print(f"\nGenerated files:")
print(f"  • {sensitivity_dir / 'alpha_sweep_summary.csv'}")
print(f"  • {sensitivity_dir / 'survival_vs_alphaCE.png'}")

if len(loaded_data) < 5:
    print("\nTo complete the analysis, run:")
    print("  python run_population.py --metallicity 0.001 --alpha_CE 1.0 --n_systems 200 --output low_Z_alpha1p0.h5")
    print("  python run_population.py --metallicity 0.001 --alpha_CE 2.0 --n_systems 200 --output low_Z_alpha2p0.h5")
    print("  python run_population.py --metallicity 0.006 --alpha_CE 1.0 --n_systems 200 --output mid_Z_alpha1p0.h5")
    print("  python run_population.py --metallicity 0.006 --alpha_CE 2.0 --n_systems 200 --output mid_Z_alpha2p0.h5")
