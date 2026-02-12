#!/usr/bin/env python3
"""
Detailed Physics Mechanism Analysis

This script performs in-depth analysis of CE physics mechanisms:
1. Shell vs Core burning donor comparison
2. Survival as function of mass ratio q = M2/M1
3. Survival as function of orbital period
4. 2D survival maps: f(q, P)
5. Binding energy analysis
6. Lambda evolution tracking

Usage:
    python physics_analysis.py
    python physics_analysis.py --include-alpha  # Include α sweep data
"""

import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.stats import beta
from scipy.ndimage import gaussian_filter
import warnings
warnings.filterwarnings('ignore')

# Create output directory
results_dir = Path('results')
physics_dir = results_dir / 'physics'
physics_dir.mkdir(parents=True, exist_ok=True)

print("="*70)
print("DETAILED PHYSICS MECHANISM ANALYSIS")
print("="*70)

# ============================================================================
# Utility Functions
# ============================================================================

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

def classify_donor_type(donor_state):
    """
    Classify donor evolutionary state into broad categories.
    
    Shell burning states typically have 'Shell' in name.
    Core burning states have 'Core' in name.
    """
    if pd.isna(donor_state):
        return 'Unknown'
    
    state_str = str(donor_state).lower()
    
    if 'shell' in state_str:
        if 'h' in state_str:
            return 'Shell H Burning'
        elif 'he' in state_str:
            return 'Shell He Burning'
        else:
            return 'Shell Burning (Other)'
    elif 'core' in state_str:
        if 'h' in state_str:
            return 'Core H Burning'
        elif 'he' in state_str:
            return 'Core He Burning'
        else:
            return 'Core Burning (Other)'
    else:
        return 'Other'

# ============================================================================
# Load Data
# ============================================================================

print("\nLoading data...")

def load_datasets(include_alpha=False):
    """Load baseline and optionally alpha sweep datasets."""
    datasets = {}
    
    # Baseline datasets
    baseline_files = {
        'Solar (α=0.5)': ('data/ce_fixed_lambda.h5', 0.014, 0.5),
        'Mid (α=0.5)': ('data/mid_Z_lambda.h5', 0.006, 0.5),
        'Low (α=0.5)': ('data/low_Z_lambda.h5', 0.001, 0.5)
    }
    
    for name, (file, Z, alpha) in baseline_files.items():
        try:
            df = pd.read_hdf(file, 'results')
            df['Z_val'] = Z
            df['alpha_CE'] = alpha
            df['dataset_name'] = name
            datasets[name] = df
            print(f"  ✓ {name}: {len(df)} systems")
        except Exception as e:
            print(f"  ✗ Error loading {file}: {e}")
    
    # Alpha sweep datasets (optional)
    if include_alpha:
        alpha_files = {
            'Low (α=1.0)': ('data/low_Z_alpha1p0.h5', 0.001, 1.0),
            'Low (α=2.0)': ('data/low_Z_alpha2p0.h5', 0.001, 2.0),
            'Mid (α=1.0)': ('data/mid_Z_alpha1p0.h5', 0.006, 1.0),
            'Mid (α=2.0)': ('data/mid_Z_alpha2p0.h5', 0.006, 2.0)
        }
        
        for name, (file, Z, alpha) in alpha_files.items():
            try:
                df = pd.read_hdf(file, 'results')
                df['Z_val'] = Z
                df['alpha_CE'] = alpha
                df['dataset_name'] = name
                datasets[name] = df
                print(f"  ✓ {name}: {len(df)} systems")
            except FileNotFoundError:
                print(f"  - {name}: Not found (optional)")
    
    if len(datasets) == 0:
        print("\n✗ No data files found!")
        exit(1)
    
    return datasets

# ============================================================================
# ANALYSIS 1: Shell vs Core Burning Donors
# ============================================================================

def analyze_shell_vs_core(datasets):
    """Compare survival for shell vs core burning donors."""
    print("\n" + "="*70)
    print("ANALYSIS 1: SHELL vs CORE BURNING DONORS")
    print("="*70)
    
    # Combine all CE events
    all_ce = []
    for name, df in datasets.items():
        ce_events = df[df['CE_occurred'] == True].copy()
        all_ce.append(ce_events)
    
    all_ce = pd.concat(all_ce, ignore_index=True)
    
    # Classify donors
    all_ce['donor_type'] = all_ce['donor_state'].apply(classify_donor_type)
    
    print(f"\nTotal CE events: {len(all_ce)}")
    print("\nDonor type distribution:")
    for donor_type in all_ce['donor_type'].value_counts().index:
        count = (all_ce['donor_type'] == donor_type).sum()
        print(f"  {donor_type}: {count}")
    
    # Analyze by donor type
    donor_results = []
    
    for donor_type in all_ce['donor_type'].unique():
        type_data = all_ce[all_ce['donor_type'] == donor_type]
        
        for Z_val in [0.014, 0.006, 0.001]:
            Z_type_data = type_data[type_data['Z_val'] == Z_val]
            
            if len(Z_type_data) == 0:
                continue
            
            n_total = len(Z_type_data)
            n_survived = Z_type_data['survived_CE'].sum()
            survival_rate = n_survived / n_total * 100
            ci_low, ci_high = wilson_ci(n_survived, n_total)
            
            # Lambda statistics
            lambda_data = Z_type_data['lambda_CE'].dropna()
            lambda_mean = lambda_data.mean() if len(lambda_data) > 0 else np.nan
            lambda_std = lambda_data.std() if len(lambda_data) > 0 else np.nan
            
            donor_results.append({
                'Donor_Type': donor_type,
                'Z': Z_val,
                'N_CE_Events': n_total,
                'N_Survived': n_survived,
                'Survival_Rate_%': survival_rate,
                'CI_Low_%': ci_low,
                'CI_High_%': ci_high,
                'Lambda_Mean': lambda_mean,
                'Lambda_Std': lambda_std
            })
    
    donor_df = pd.DataFrame(donor_results)
    donor_df.to_csv(physics_dir / 'shell_vs_core_analysis.csv', index=False)
    print(f"\n✓ Saved: {physics_dir / 'shell_vs_core_analysis.csv'}")
    
    # Print summary
    print("\nSurvival by donor type and metallicity:")
    for _, row in donor_df.iterrows():
        print(f"\n{row['Donor_Type']} (Z={row['Z']}):")
        print(f"  Events: {row['N_CE_Events']}")
        print(f"  Survival: {row['Survival_Rate_%']:.1f}% (CI: {row['CI_Low_%']:.1f}-{row['CI_High_%']:.1f}%)")
        print(f"  Lambda: {row['Lambda_Mean']:.3f} ± {row['Lambda_Std']:.3f}")
    
    return donor_df, all_ce

# ============================================================================
# ANALYSIS 2: Survival vs Mass Ratio
# ============================================================================

def analyze_mass_ratio(all_ce):
    """Analyze survival as function of mass ratio q."""
    print("\n" + "="*70)
    print("ANALYSIS 2: SURVIVAL vs MASS RATIO (q)")
    print("="*70)
    
    # Define mass ratio bins
    q_bins = np.linspace(0.4, 1.0, 7)  # 6 bins from 0.4 to 1.0
    
    q_results = []
    
    for i in range(len(q_bins) - 1):
        q_min = q_bins[i]
        q_max = q_bins[i+1]
        
        mask = (all_ce['q_initial'] >= q_min) & (all_ce['q_initial'] < q_max)
        bin_data = all_ce[mask]
        
        if len(bin_data) == 0:
            continue
        
        for Z_val in [0.014, 0.006, 0.001]:
            Z_data = bin_data[bin_data['Z_val'] == Z_val]
            
            if len(Z_data) == 0:
                continue
            
            n_total = len(Z_data)
            n_survived = Z_data['survived_CE'].sum()
            survival_rate = n_survived / n_total * 100
            ci_low, ci_high = wilson_ci(n_survived, n_total)
            
            q_results.append({
                'q_min': q_min,
                'q_max': q_max,
                'q_center': (q_min + q_max) / 2,
                'Z': Z_val,
                'N_Systems': n_total,
                'N_Survived': n_survived,
                'Survival_Rate_%': survival_rate,
                'CI_Low_%': ci_low,
                'CI_High_%': ci_high
            })
    
    q_df = pd.DataFrame(q_results)
    q_df.to_csv(physics_dir / 'survival_vs_mass_ratio.csv', index=False)
    print(f"\n✓ Saved: {physics_dir / 'survival_vs_mass_ratio.csv'}")
    
    print("\nSurvival vs mass ratio:")
    for Z_val in [0.014, 0.006, 0.001]:
        Z_data = q_df[q_df['Z'] == Z_val]
        if len(Z_data) > 0:
            print(f"\nZ = {Z_val}:")
            for _, row in Z_data.iterrows():
                print(f"  q ∈ [{row['q_min']:.2f}, {row['q_max']:.2f}]: "
                      f"{row['Survival_Rate_%']:.1f}% (n={row['N_Systems']})")
    
    return q_df

# ============================================================================
# ANALYSIS 3: Survival vs Orbital Period
# ============================================================================

def analyze_orbital_period(all_ce):
    """Analyze survival as function of initial orbital period."""
    print("\n" + "="*70)
    print("ANALYSIS 3: SURVIVAL vs ORBITAL PERIOD")
    print("="*70)
    
    # Define period bins (log-spaced)
    P_bins = np.logspace(np.log10(50), np.log10(5000), 7)
    
    P_results = []
    
    for i in range(len(P_bins) - 1):
        P_min = P_bins[i]
        P_max = P_bins[i+1]
        
        mask = (all_ce['P_initial'] >= P_min) & (all_ce['P_initial'] < P_max)
        bin_data = all_ce[mask]
        
        if len(bin_data) == 0:
            continue
        
        for Z_val in [0.014, 0.006, 0.001]:
            Z_data = bin_data[bin_data['Z_val'] == Z_val]
            
            if len(Z_data) == 0:
                continue
            
            n_total = len(Z_data)
            n_survived = Z_data['survived_CE'].sum()
            survival_rate = n_survived / n_total * 100
            ci_low, ci_high = wilson_ci(n_survived, n_total)
            
            P_results.append({
                'P_min': P_min,
                'P_max': P_max,
                'P_center': np.sqrt(P_min * P_max),  # Geometric mean
                'Z': Z_val,
                'N_Systems': n_total,
                'N_Survived': n_survived,
                'Survival_Rate_%': survival_rate,
                'CI_Low_%': ci_low,
                'CI_High_%': ci_high
            })
    
    P_df = pd.DataFrame(P_results)
    P_df.to_csv(physics_dir / 'survival_vs_period.csv', index=False)
    print(f"\n✓ Saved: {physics_dir / 'survival_vs_period.csv'}")
    
    print("\nSurvival vs orbital period:")
    for Z_val in [0.014, 0.006, 0.001]:
        Z_data = P_df[P_df['Z'] == Z_val]
        if len(Z_data) > 0:
            print(f"\nZ = {Z_val}:")
            for _, row in Z_data.iterrows():
                print(f"  P ∈ [{row['P_min']:.0f}, {row['P_max']:.0f}] days: "
                      f"{row['Survival_Rate_%']:.1f}% (n={row['N_Systems']})")
    
    return P_df

# ============================================================================
# ANALYSIS 4: 2D Survival Maps
# ============================================================================

def create_2d_survival_maps(all_ce):
    """Create 2D survival probability maps: f(q, P)."""
    print("\n" + "="*70)
    print("ANALYSIS 4: 2D SURVIVAL MAPS")
    print("="*70)
    
    # Define 2D grid
    q_bins = np.linspace(0.4, 1.0, 8)
    P_bins = np.logspace(np.log10(50), np.log10(5000), 8)
    
    # Create figure with subplots for each metallicity
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    for idx, (Z_val, Z_label) in enumerate([(0.014, 'Solar'), (0.006, 'Mid'), (0.001, 'Low')]):
        Z_data = all_ce[all_ce['Z_val'] == Z_val]
        
        # Create 2D histogram
        survival_map = np.zeros((len(q_bins)-1, len(P_bins)-1))
        count_map = np.zeros((len(q_bins)-1, len(P_bins)-1))
        
        for i in range(len(q_bins) - 1):
            for j in range(len(P_bins) - 1):
                mask = ((Z_data['q_initial'] >= q_bins[i]) & 
                       (Z_data['q_initial'] < q_bins[i+1]) &
                       (Z_data['P_initial'] >= P_bins[j]) & 
                       (Z_data['P_initial'] < P_bins[j+1]))
                
                bin_data = Z_data[mask]
                count_map[i, j] = len(bin_data)
                
                if len(bin_data) > 0:
                    survival_map[i, j] = bin_data['survived_CE'].sum() / len(bin_data) * 100
                else:
                    survival_map[i, j] = np.nan
        
        # Smooth for visualization (only where we have data)
        survival_map_smooth = survival_map.copy()
        mask_valid = ~np.isnan(survival_map)
        if mask_valid.sum() > 0:
            survival_map_smooth[mask_valid] = gaussian_filter(
                survival_map[mask_valid].reshape(-1), sigma=0.5
            ).reshape(-1)
        
        # Plot
        ax = axes[idx]
        im = ax.imshow(survival_map.T, origin='lower', aspect='auto', 
                      cmap='RdYlGn', vmin=0, vmax=100, interpolation='nearest')
        
        ax.set_xlabel('Mass Ratio (q)', fontsize=12, weight='bold')
        ax.set_ylabel('Orbital Period (days)', fontsize=12, weight='bold')
        ax.set_title(f'{Z_label} Z (Z={Z_val})', fontsize=14, weight='bold')
        
        # Set ticks
        ax.set_xticks(np.arange(len(q_bins)-1))
        ax.set_xticklabels([f'{q:.2f}' for q in (q_bins[:-1] + q_bins[1:]) / 2], rotation=45)
        ax.set_yticks(np.arange(len(P_bins)-1))
        ax.set_yticklabels([f'{int(p):.0f}' for p in np.sqrt(P_bins[:-1] * P_bins[1:])])
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Survival Probability (%)', fontsize=10)
        
        # Overlay counts
        for i in range(len(q_bins)-1):
            for j in range(len(P_bins)-1):
                if count_map[i, j] > 0:
                    ax.text(i, j, f'{int(count_map[i, j])}', 
                           ha='center', va='center', fontsize=8, 
                           color='white' if survival_map[i, j] < 50 else 'black')
    
    plt.tight_layout()
    plt.savefig(physics_dir / '2d_survival_maps.png', dpi=300, bbox_inches='tight')
    print(f"\n✓ Saved: {physics_dir / '2d_survival_maps.png'}")

# ============================================================================
# FIGURES
# ============================================================================

def create_physics_figures(donor_df, q_df, P_df):
    """Create comprehensive physics analysis figures."""
    print("\n" + "="*70)
    print("GENERATING FIGURES")
    print("="*70)
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Plot 1: Shell vs Core survival
    ax = axes[0, 0]
    donor_types = ['Shell H Burning', 'Shell He Burning', 'Core H Burning', 'Core He Burning']
    plot_data = donor_df[donor_df['Donor_Type'].isin(donor_types)]
    
    if len(plot_data) > 0:
        x_pos = np.arange(len(donor_types))
        width = 0.25
        
        for i, (Z_val, color, label) in enumerate([(0.014, 'orange', 'Solar'),
                                                     (0.006, 'blue', 'Mid'),
                                                     (0.001, 'purple', 'Low')]):
            Z_data = plot_data[plot_data['Z'] == Z_val]
            survival_rates = [
                Z_data[Z_data['Donor_Type'] == dt]['Survival_Rate_%'].values[0] 
                if len(Z_data[Z_data['Donor_Type'] == dt]) > 0 else 0
                for dt in donor_types
            ]
            
            offset = (i - 1) * width
            ax.bar(x_pos + offset, survival_rates, width, label=f'{label} Z',
                  color=color, alpha=0.7, edgecolor='black', linewidth=1.5)
        
        ax.set_xlabel('Donor Evolutionary State', fontsize=12, weight='bold')
        ax.set_ylabel('Survival Rate (%)', fontsize=12, weight='bold')
        ax.set_title('Shell vs Core Burning Donors', fontsize=14, weight='bold')
        ax.set_xticks(x_pos)
        ax.set_xticklabels([dt.replace(' Burning', '') for dt in donor_types], 
                          rotation=45, ha='right', fontsize=10)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3, axis='y')
    
    # Plot 2: Survival vs Mass Ratio
    ax = axes[0, 1]
    for Z_val, color, label in [(0.014, 'orange', 'Solar'), 
                                 (0.006, 'blue', 'Mid'), 
                                 (0.001, 'purple', 'Low')]:
        Z_data = q_df[q_df['Z'] == Z_val]
        if len(Z_data) > 0:
            ax.plot(Z_data['q_center'], Z_data['Survival_Rate_%'], 
                   marker='o', linewidth=2.5, markersize=8, label=f'{label} Z',
                   color=color, markeredgecolor='black', markeredgewidth=1.5)
    
    ax.set_xlabel('Mass Ratio (q = M₂/M₁)', fontsize=12, weight='bold')
    ax.set_ylabel('Survival Rate (%)', fontsize=12, weight='bold')
    ax.set_title('Survival vs Mass Ratio', fontsize=14, weight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    # Plot 3: Survival vs Period
    ax = axes[1, 0]
    for Z_val, color, label in [(0.014, 'orange', 'Solar'),
                                 (0.006, 'blue', 'Mid'),
                                 (0.001, 'purple', 'Low')]:
        Z_data = P_df[P_df['Z'] == Z_val]
        if len(Z_data) > 0:
            ax.semilogx(Z_data['P_center'], Z_data['Survival_Rate_%'],
                       marker='s', linewidth=2.5, markersize=8, label=f'{label} Z',
                       color=color, markeredgecolor='black', markeredgewidth=1.5)
    
    ax.set_xlabel('Initial Orbital Period (days)', fontsize=12, weight='bold')
    ax.set_ylabel('Survival Rate (%)', fontsize=12, weight='bold')
    ax.set_title('Survival vs Orbital Period', fontsize=14, weight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, which='both')
    
    # Plot 4: Lambda by donor type
    ax = axes[1, 1]
    plot_data = donor_df[donor_df['Donor_Type'].isin(donor_types)]
    
    if len(plot_data) > 0:
        x_pos = np.arange(len(donor_types))
        
        # Average lambda across metallicities
        lambda_means = []
        lambda_stds = []
        for dt in donor_types:
            dt_data = plot_data[plot_data['Donor_Type'] == dt]
            lambda_means.append(dt_data['Lambda_Mean'].mean())
            lambda_stds.append(dt_data['Lambda_Std'].mean())
        
        ax.bar(x_pos, lambda_means, color='steelblue', alpha=0.7,
              edgecolor='black', linewidth=2, yerr=lambda_stds, capsize=6)
        ax.axhline(0.5, color='red', linestyle='--', linewidth=2, 
                  label='Classical: λ=0.5', alpha=0.7)
        
        ax.set_xlabel('Donor Evolutionary State', fontsize=12, weight='bold')
        ax.set_ylabel('Mean Lambda (λ)', fontsize=12, weight='bold')
        ax.set_title('Lambda by Donor Type', fontsize=14, weight='bold')
        ax.set_xticks(x_pos)
        ax.set_xticklabels([dt.replace(' Burning', '') for dt in donor_types],
                          rotation=45, ha='right', fontsize=10)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(physics_dir / 'physics_analysis.png', dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {physics_dir / 'physics_analysis.png'}")

# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Detailed physics mechanism analysis'
    )
    parser.add_argument('--include-alpha', action='store_true',
                       help='Include alpha sweep data in analysis')
    
    args = parser.parse_args()
    
    # Load data
    datasets = load_datasets(include_alpha=args.include_alpha)
    
    # Run analyses
    donor_df, all_ce = analyze_shell_vs_core(datasets)
    q_df = analyze_mass_ratio(all_ce)
    P_df = analyze_orbital_period(all_ce)
    create_2d_survival_maps(all_ce)
    
    # Create figures
    create_physics_figures(donor_df, q_df, P_df)
    
    # Summary
    print("\n" + "="*70)
    print("PHYSICS ANALYSIS COMPLETE")
    print("="*70)
    print("\nGenerated files:")
    print(f"  • {physics_dir / 'shell_vs_core_analysis.csv'}")
    print(f"  • {physics_dir / 'survival_vs_mass_ratio.csv'}")
    print(f"  • {physics_dir / 'survival_vs_period.csv'}")
    print(f"  • {physics_dir / '2d_survival_maps.png'}")
    print(f"  • {physics_dir / 'physics_analysis.png'}")

if __name__ == '__main__':
    main()
