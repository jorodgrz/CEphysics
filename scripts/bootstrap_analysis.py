#!/usr/bin/env python3
"""
Bootstrap Resampling Analysis for Statistical Robustness

This script performs bootstrap resampling (10k iterations) to provide
robust uncertainty estimates for:
- CE occurrence rates
- Survival rates  
- Lambda distributions
- Survival probability as function of lambda

The bootstrap provides non-parametric confidence intervals that don't
assume any particular distribution shape.

Usage:
    python bootstrap_analysis.py
    python bootstrap_analysis.py --n_boot 5000  # Faster (5k iterations)
    python bootstrap_analysis.py --n_boot 20000 # More precise (20k iterations)
"""

import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

# Create output directory
results_dir = Path('results')
bootstrap_dir = results_dir / 'bootstrap'
bootstrap_dir.mkdir(parents=True, exist_ok=True)

print("="*70)
print("BOOTSTRAP RESAMPLING ANALYSIS")
print("="*70)

# ============================================================================
# Bootstrap Functions
# ============================================================================

def bootstrap_rate(data, n_iterations=10000, alpha=0.05):
    """
    Bootstrap confidence interval for a rate (proportion).
    
    Parameters:
    -----------
    data : array-like of bool
        Success/failure outcomes
    n_iterations : int
        Number of bootstrap samples
    alpha : float
        Significance level (0.05 = 95% CI)
    
    Returns:
    --------
    dict with mean, std, CI_low, CI_high (all as percentages)
    """
    data = np.array(data)
    n = len(data)
    
    if n == 0:
        return {'mean': 0.0, 'std': 0.0, 'CI_low': 0.0, 'CI_high': 0.0}
    
    # Bootstrap sampling
    bootstrap_rates = []
    for _ in range(n_iterations):
        sample = np.random.choice(data, size=n, replace=True)
        bootstrap_rates.append(sample.mean() * 100)
    
    bootstrap_rates = np.array(bootstrap_rates)
    
    # Calculate statistics
    mean_rate = bootstrap_rates.mean()
    std_rate = bootstrap_rates.std()
    ci_low = np.percentile(bootstrap_rates, alpha/2 * 100)
    ci_high = np.percentile(bootstrap_rates, (1 - alpha/2) * 100)
    
    return {
        'mean': mean_rate,
        'std': std_rate,
        'CI_low': ci_low,
        'CI_high': ci_high,
        'distribution': bootstrap_rates
    }

def bootstrap_mean(data, n_iterations=10000, alpha=0.05):
    """
    Bootstrap confidence interval for a mean value.
    
    Parameters:
    -----------
    data : array-like
        Numerical values
    n_iterations : int
        Number of bootstrap samples
    alpha : float
        Significance level
    
    Returns:
    --------
    dict with mean, std, CI_low, CI_high
    """
    data = np.array(data)
    data = data[~np.isnan(data)]  # Remove NaN
    n = len(data)
    
    if n == 0:
        return {'mean': np.nan, 'std': np.nan, 'CI_low': np.nan, 'CI_high': np.nan}
    
    # Bootstrap sampling
    bootstrap_means = []
    for _ in range(n_iterations):
        sample = np.random.choice(data, size=n, replace=True)
        bootstrap_means.append(sample.mean())
    
    bootstrap_means = np.array(bootstrap_means)
    
    # Calculate statistics
    mean_val = bootstrap_means.mean()
    std_val = bootstrap_means.std()
    ci_low = np.percentile(bootstrap_means, alpha/2 * 100)
    ci_high = np.percentile(bootstrap_means, (1 - alpha/2) * 100)
    
    return {
        'mean': mean_val,
        'std': std_val,
        'CI_low': ci_low,
        'CI_high': ci_high,
        'distribution': bootstrap_means
    }

def bootstrap_survival_by_lambda(ce_data, lambda_bins, n_iterations=10000):
    """
    Bootstrap survival probability in lambda bins.
    
    Parameters:
    -----------
    ce_data : DataFrame
        CE events with 'lambda_CE' and 'survived_CE'
    lambda_bins : array
        Bin edges for lambda
    n_iterations : int
        Number of bootstrap samples
    
    Returns:
    --------
    DataFrame with binned survival probabilities and CIs
    """
    n = len(ce_data)
    n_bins = len(lambda_bins) - 1
    
    # Pre-allocate results
    bin_results = []
    
    for i in range(n_bins):
        bin_min = lambda_bins[i]
        bin_max = lambda_bins[i+1]
        bin_label = f"{bin_min:.2f}-{bin_max:.2f}"
        
        # Get data in this bin
        mask = (ce_data['lambda_CE'] >= bin_min) & (ce_data['lambda_CE'] < bin_max)
        bin_data = ce_data[mask]
        
        if len(bin_data) == 0:
            continue
        
        # Bootstrap this bin
        bootstrap_rates = []
        for _ in range(n_iterations):
            sample = bin_data.sample(n=len(bin_data), replace=True)
            survival_rate = sample['survived_CE'].mean() * 100
            bootstrap_rates.append(survival_rate)
        
        bootstrap_rates = np.array(bootstrap_rates)
        
        bin_results.append({
            'Lambda_Bin': bin_label,
            'Lambda_Min': bin_min,
            'Lambda_Max': bin_max,
            'N_Systems': len(bin_data),
            'Mean_Survival_%': bootstrap_rates.mean(),
            'Std_Survival_%': bootstrap_rates.std(),
            'CI_Low_%': np.percentile(bootstrap_rates, 2.5),
            'CI_High_%': np.percentile(bootstrap_rates, 97.5)
        })
    
    return pd.DataFrame(bin_results)

# ============================================================================
# Load Data
# ============================================================================

print("\nLoading data...")
datasets = {}
try:
    datasets['Solar'] = pd.read_hdf('data/ce_fixed_lambda.h5', 'results')
    datasets['Mid'] = pd.read_hdf('data/mid_Z_lambda.h5', 'results')
    datasets['Low'] = pd.read_hdf('data/low_Z_lambda.h5', 'results')
    print("✓ All datasets loaded")
except Exception as e:
    print(f"✗ Error loading data: {e}")
    exit(1)

# Add metallicity values
datasets['Solar']['Z_val'] = 0.014
datasets['Mid']['Z_val'] = 0.006
datasets['Low']['Z_val'] = 0.001

# ============================================================================
# ANALYSIS 1: CE Occurrence Rates
# ============================================================================

print("\n" + "="*70)
print("ANALYSIS 1: CE OCCURRENCE RATES (Bootstrap)")
print("="*70)

def main(n_boot=10000):
    ce_rate_results = []
    
    for name, df in datasets.items():
        print(f"\nBootstrapping {name} metallicity (n={len(df)})...")
        
        # CE occurrence
        ce_occurred = df['CE_occurred'].fillna(False).values
        ce_stats = bootstrap_rate(ce_occurred, n_iterations=n_boot)
        
        ce_rate_results.append({
            'Metallicity': name,
            'Z': df['Z_val'].iloc[0],
            'Total_Systems': len(df),
            'CE_Rate_Mean_%': ce_stats['mean'],
            'CE_Rate_Std_%': ce_stats['std'],
            'CE_Rate_CI_Low_%': ce_stats['CI_low'],
            'CE_Rate_CI_High_%': ce_stats['CI_high']
        })
        
        print(f"  CE rate: {ce_stats['mean']:.1f}% ± {ce_stats['std']:.1f}%")
        print(f"  95% CI: [{ce_stats['CI_low']:.1f}%, {ce_stats['CI_high']:.1f}%]")
    
    ce_rate_df = pd.DataFrame(ce_rate_results)
    ce_rate_df.to_csv(bootstrap_dir / 'ce_rates_bootstrap.csv', index=False)
    print(f"\n✓ Saved: {bootstrap_dir / 'ce_rates_bootstrap.csv'}")
    
    # ============================================================================
    # ANALYSIS 2: CE Survival Rates
    # ============================================================================
    
    print("\n" + "="*70)
    print("ANALYSIS 2: CE SURVIVAL RATES (Bootstrap)")
    print("="*70)
    
    survival_results = []
    
    for name, df in datasets.items():
        # Filter to CE events only
        ce_events = df[df['CE_occurred'] == True]
        
        if len(ce_events) == 0:
            print(f"\n{name}: No CE events")
            continue
        
        print(f"\nBootstrapping {name} survival (n={len(ce_events)} CE events)...")
        
        survived = ce_events['survived_CE'].fillna(False).values
        survival_stats = bootstrap_rate(survived, n_iterations=n_boot)
        
        survival_results.append({
            'Metallicity': name,
            'Z': df['Z_val'].iloc[0],
            'CE_Events': len(ce_events),
            'Survival_Mean_%': survival_stats['mean'],
            'Survival_Std_%': survival_stats['std'],
            'Survival_CI_Low_%': survival_stats['CI_low'],
            'Survival_CI_High_%': survival_stats['CI_high']
        })
        
        print(f"  Survival: {survival_stats['mean']:.1f}% ± {survival_stats['std']:.1f}%")
        print(f"  95% CI: [{survival_stats['CI_low']:.1f}%, {survival_stats['CI_high']:.1f}%]")
    
    survival_df = pd.DataFrame(survival_results)
    survival_df.to_csv(bootstrap_dir / 'survival_rates_bootstrap.csv', index=False)
    print(f"\n✓ Saved: {bootstrap_dir / 'survival_rates_bootstrap.csv'}")
    
    # ============================================================================
    # ANALYSIS 3: Lambda Distributions
    # ============================================================================
    
    print("\n" + "="*70)
    print("ANALYSIS 3: LAMBDA DISTRIBUTIONS (Bootstrap)")
    print("="*70)
    
    lambda_results = []
    
    for name, df in datasets.items():
        # Filter to CE events with lambda
        ce_with_lambda = df[(df['CE_occurred'] == True) & (df['lambda_CE'].notna())]
        
        if len(ce_with_lambda) == 0:
            print(f"\n{name}: No lambda data")
            continue
        
        print(f"\nBootstrapping {name} lambda (n={len(ce_with_lambda)})...")
        
        lambda_vals = ce_with_lambda['lambda_CE'].values
        lambda_stats = bootstrap_mean(lambda_vals, n_iterations=n_boot)
        
        lambda_results.append({
            'Metallicity': name,
            'Z': df['Z_val'].iloc[0],
            'N_Systems': len(ce_with_lambda),
            'Lambda_Mean': lambda_stats['mean'],
            'Lambda_Std': lambda_stats['std'],
            'Lambda_CI_Low': lambda_stats['CI_low'],
            'Lambda_CI_High': lambda_stats['CI_high']
        })
        
        print(f"  Lambda: {lambda_stats['mean']:.3f} ± {lambda_stats['std']:.3f}")
        print(f"  95% CI: [{lambda_stats['CI_low']:.3f}, {lambda_stats['CI_high']:.3f}]")
    
    lambda_df = pd.DataFrame(lambda_results)
    lambda_df.to_csv(bootstrap_dir / 'lambda_bootstrap.csv', index=False)
    print(f"\n✓ Saved: {bootstrap_dir / 'lambda_bootstrap.csv'}")
    
    # ============================================================================
    # ANALYSIS 4: Survival vs Lambda (Binned)
    # ============================================================================
    
    print("\n" + "="*70)
    print("ANALYSIS 4: SURVIVAL VS LAMBDA (Bootstrap)")
    print("="*70)
    
    # Combine all CE events
    all_ce = pd.concat([
        datasets['Solar'][(datasets['Solar']['CE_occurred'] == True) & 
                         (datasets['Solar']['lambda_CE'].notna())],
        datasets['Mid'][(datasets['Mid']['CE_occurred'] == True) & 
                       (datasets['Mid']['lambda_CE'].notna())],
        datasets['Low'][(datasets['Low']['CE_occurred'] == True) & 
                       (datasets['Low']['lambda_CE'].notna())]
    ])
    
    print(f"\nCombined CE events: {len(all_ce)}")
    
    # Define lambda bins
    lambda_bins = np.array([0, 0.03, 0.06, 0.10, 0.15, 0.25, 1.0])
    
    print(f"Bootstrapping survival in {len(lambda_bins)-1} lambda bins...")
    survival_by_lambda = bootstrap_survival_by_lambda(all_ce, lambda_bins, n_iterations=n_boot)
    survival_by_lambda.to_csv(bootstrap_dir / 'survival_vs_lambda_bootstrap.csv', index=False)
    print(f"\n✓ Saved: {bootstrap_dir / 'survival_vs_lambda_bootstrap.csv'}")
    
    for _, row in survival_by_lambda.iterrows():
        print(f"\nλ ∈ [{row['Lambda_Min']:.2f}, {row['Lambda_Max']:.2f}] (n={row['N_Systems']}):")
        print(f"  Survival: {row['Mean_Survival_%']:.1f}% ± {row['Std_Survival_%']:.1f}%")
        print(f"  95% CI: [{row['CI_Low_%']:.1f}%, {row['CI_High_%']:.1f}%]")
    
    # ============================================================================
    # FIGURES
    # ============================================================================
    
    print("\n" + "="*70)
    print("GENERATING FIGURES")
    print("="*70)
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Plot 1: CE Occurrence Rates with Bootstrap CIs
    ax = axes[0, 0]
    x = np.arange(len(ce_rate_df))
    ax.bar(x, ce_rate_df['CE_Rate_Mean_%'], color='steelblue', alpha=0.7, 
           edgecolor='black', linewidth=2)
    ax.errorbar(x, ce_rate_df['CE_Rate_Mean_%'],
                yerr=[ce_rate_df['CE_Rate_Mean_%'] - ce_rate_df['CE_Rate_CI_Low_%'],
                      ce_rate_df['CE_Rate_CI_High_%'] - ce_rate_df['CE_Rate_Mean_%']],
                fmt='none', ecolor='black', capsize=8, capthick=2)
    ax.set_xticks(x)
    ax.set_xticklabels(ce_rate_df['Metallicity'])
    ax.set_ylabel('CE Occurrence Rate (%)', fontsize=12, weight='bold')
    ax.set_title(f'CE Rates with Bootstrap CIs (n={n_boot})', fontsize=14, weight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    
    # Plot 2: Survival Rates with Bootstrap CIs
    ax = axes[0, 1]
    x = np.arange(len(survival_df))
    colors = ['green' if rate > 0 else 'red' for rate in survival_df['Survival_Mean_%']]
    ax.bar(x, survival_df['Survival_Mean_%'], color=colors, alpha=0.7,
           edgecolor='black', linewidth=2)
    ax.errorbar(x, survival_df['Survival_Mean_%'],
                yerr=[survival_df['Survival_Mean_%'] - survival_df['Survival_CI_Low_%'],
                      survival_df['Survival_CI_High_%'] - survival_df['Survival_Mean_%']],
                fmt='none', ecolor='black', capsize=8, capthick=2)
    ax.set_xticks(x)
    ax.set_xticklabels(survival_df['Metallicity'])
    ax.set_ylabel('CE Survival Rate (%)', fontsize=12, weight='bold')
    ax.set_title(f'Survival Rates with Bootstrap CIs (n={n_boot})', fontsize=14, weight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    
    # Plot 3: Lambda with Bootstrap CIs
    ax = axes[1, 0]
    x = np.arange(len(lambda_df))
    ax.errorbar(x, lambda_df['Lambda_Mean'],
                yerr=[lambda_df['Lambda_Mean'] - lambda_df['Lambda_CI_Low'],
                      lambda_df['Lambda_CI_High'] - lambda_df['Lambda_Mean']],
                marker='o', markersize=12, linewidth=2.5, capsize=8, capthick=2,
                color='steelblue', markerfacecolor='orange', 
                markeredgecolor='black', markeredgewidth=2)
    ax.axhline(0.5, color='red', linestyle='--', linewidth=2, alpha=0.7, label='Classical: λ=0.5')
    ax.set_xticks(x)
    ax.set_xticklabels(lambda_df['Metallicity'])
    ax.set_ylabel('Mean Lambda (λ)', fontsize=12, weight='bold')
    ax.set_title(f'Lambda with Bootstrap CIs (n={n_boot})', fontsize=14, weight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    # Plot 4: Survival vs Lambda (Binned) with Bootstrap CIs
    ax = axes[1, 1]
    x = np.arange(len(survival_by_lambda))
    ax.bar(x, survival_by_lambda['Mean_Survival_%'], color='purple', alpha=0.7,
           edgecolor='black', linewidth=2)
    ax.errorbar(x, survival_by_lambda['Mean_Survival_%'],
                yerr=[survival_by_lambda['Mean_Survival_%'] - survival_by_lambda['CI_Low_%'],
                      survival_by_lambda['CI_High_%'] - survival_by_lambda['Mean_Survival_%']],
                fmt='none', ecolor='black', capsize=6, capthick=2)
    ax.set_xticks(x)
    ax.set_xticklabels(survival_by_lambda['Lambda_Bin'], rotation=45, ha='right')
    ax.set_xlabel('Lambda Bin', fontsize=12, weight='bold')
    ax.set_ylabel('Survival Probability (%)', fontsize=12, weight='bold')
    ax.set_title(f'Survival vs Lambda (n={n_boot})', fontsize=14, weight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add sample sizes
    for i, n in enumerate(survival_by_lambda['N_Systems']):
        ax.text(i, -5, f'n={n}', ha='center', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(bootstrap_dir / 'bootstrap_analysis.png', dpi=300, bbox_inches='tight')
    print(f"\n✓ Saved: {bootstrap_dir / 'bootstrap_analysis.png'}")
    
    # ============================================================================
    # SUMMARY
    # ============================================================================
    
    print("\n" + "="*70)
    print("BOOTSTRAP ANALYSIS COMPLETE")
    print("="*70)
    print(f"\nBootstrap iterations: {n_boot}")
    print(f"Confidence level: 95%")
    print("\nGenerated files:")
    print(f"  • {bootstrap_dir / 'ce_rates_bootstrap.csv'}")
    print(f"  • {bootstrap_dir / 'survival_rates_bootstrap.csv'}")
    print(f"  • {bootstrap_dir / 'lambda_bootstrap.csv'}")
    print(f"  • {bootstrap_dir / 'survival_vs_lambda_bootstrap.csv'}")
    print(f"  • {bootstrap_dir / 'bootstrap_analysis.png'}")
    print("\nKey advantage of bootstrap over analytical CIs:")
    print("  - No distributional assumptions")
    print("  - Robust for small samples")
    print("  - Captures full uncertainty including correlations")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Bootstrap resampling for robust uncertainty estimates'
    )
    parser.add_argument('--n_boot', type=int, default=10000,
                       help='Number of bootstrap iterations (default: 10000)')
    
    args = parser.parse_args()
    
    print(f"\nBootstrap iterations: {args.n_boot}")
    main(n_boot=args.n_boot)
