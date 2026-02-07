#!/usr/bin/env python3
"""
Mechanism analysis: Survival vs Lambda and Evolutionary State

This script analyzes the physical mechanisms behind CE survival by examining:
1. Survival probability as a function of lambda (λ)
2. Role of evolutionary state (donor stellar type)
3. Lambda distributions stratified by outcome

Usage:
    python analyze_mechanisms.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.stats import beta

# Create output directory
results_dir = Path('results')
sensitivity_dir = results_dir / 'sensitivity'
sensitivity_dir.mkdir(parents=True, exist_ok=True)

print("="*70)
print("MECHANISM ANALYSIS - SURVIVAL VS LAMBDA")
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

# Load all datasets
print("\nLoading data...")
try:
    solar_Z = pd.read_hdf('ce_fixed_lambda.h5', 'results')
    mid_Z = pd.read_hdf('mid_Z_lambda.h5', 'results')
    low_Z = pd.read_hdf('low_Z_lambda.h5', 'results')
    print("✓ Data loaded successfully")
except Exception as e:
    print(f"✗ Error: {e}")
    exit(1)

# Combine all CE events with lambda data
solar_ce = solar_Z[(solar_Z['CE_occurred'] == True) & (solar_Z['lambda_CE'].notna())].assign(Z_label='Solar (0.014)', Z_val=0.014)
mid_ce = mid_Z[(mid_Z['CE_occurred'] == True) & (mid_Z['lambda_CE'].notna())].assign(Z_label='Mid (0.006)', Z_val=0.006)
low_ce = low_Z[(low_Z['CE_occurred'] == True) & (low_Z['lambda_CE'].notna())].assign(Z_label='Low (0.001)', Z_val=0.001)

all_ce = pd.concat([solar_ce, mid_ce, low_ce], ignore_index=True)

print(f"\nTotal CE events with lambda data: {len(all_ce)}")
print(f"  Solar Z: {len(solar_ce)}")
print(f"  Mid Z: {len(mid_ce)}")
print(f"  Low Z: {len(low_ce)}")

# ============================================================================
# ANALYSIS 1: Survival vs Lambda (Binned)
# ============================================================================
print("\n" + "="*70)
print("ANALYSIS 1: SURVIVAL PROBABILITY VS LAMBDA")
print("="*70)

# Define lambda bins
lambda_bins = [0, 0.03, 0.06, 0.10, 0.15, 0.25, 1.0]
lambda_labels = ['0-0.03', '0.03-0.06', '0.06-0.10', '0.10-0.15', '0.15-0.25', '>0.25']

# Bin lambda values
all_ce['lambda_bin'] = pd.cut(all_ce['lambda_CE'], bins=lambda_bins, labels=lambda_labels, include_lowest=True)

# Calculate survival by bin
binned_results = []
for bin_label in lambda_labels:
    bin_data = all_ce[all_ce['lambda_bin'] == bin_label]
    if len(bin_data) > 0:
        n_total = len(bin_data)
        n_survived = bin_data['survived_CE'].sum()
        survival_rate = n_survived / n_total * 100
        ci_low, ci_high = wilson_ci(n_survived, n_total)
        
        binned_results.append({
            'Lambda_Bin': bin_label,
            'N_Systems': n_total,
            'N_Survived': n_survived,
            'Survival_Rate_%': survival_rate,
            'CI_Low_%': ci_low,
            'CI_High_%': ci_high,
            'Mean_Lambda': bin_data['lambda_CE'].mean()
        })
        
        print(f"\nλ = {bin_label}:")
        print(f"  Systems: {n_total}")
        print(f"  Survived: {n_survived}")
        print(f"  Rate: {survival_rate:.1f}% (95% CI: {ci_low:.1f}-{ci_high:.1f}%)")

binned_df = pd.DataFrame(binned_results)
binned_df.to_csv(sensitivity_dir / 'lambda_binned_survival.csv', index=False)
print(f"\n✓ Saved: {sensitivity_dir / 'lambda_binned_survival.csv'}")

# ============================================================================
# ANALYSIS 2: Survival by Evolutionary State
# ============================================================================
print("\n" + "="*70)
print("ANALYSIS 2: SURVIVAL BY DONOR EVOLUTIONARY STATE")
print("="*70)

# Group by metallicity and donor state
state_results = []
for Z_val, Z_label in [(0.014, 'Solar'), (0.006, 'Mid'), (0.001, 'Low')]:
    Z_data = all_ce[all_ce['Z_val'] == Z_val]
    
    for state in Z_data['donor_state'].dropna().unique():
        state_data = Z_data[Z_data['donor_state'] == state]
        n_total = len(state_data)
        n_survived = state_data['survived_CE'].sum()
        survival_rate = n_survived / n_total * 100 if n_total > 0 else 0
        ci_low, ci_high = wilson_ci(n_survived, n_total)
        
        state_results.append({
            'Metallicity': Z_label,
            'Z': Z_val,
            'Donor_State': state,
            'N_CE_Events': n_total,
            'N_Survived': n_survived,
            'Survival_Rate_%': survival_rate,
            'CI_Low_%': ci_low,
            'CI_High_%': ci_high,
            'Lambda_Mean': state_data['lambda_CE'].mean(),
            'Lambda_Std': state_data['lambda_CE'].std()
        })

state_df = pd.DataFrame(state_results)
state_df.to_csv(sensitivity_dir / 'donor_state_stratified.csv', index=False)
print(f"\n✓ Saved: {sensitivity_dir / 'donor_state_stratified.csv'}")

print("\nSurvival by donor state:")
for _, row in state_df.iterrows():
    print(f"\n{row['Metallicity']} Z - {row['Donor_State']}:")
    print(f"  CE events: {row['N_CE_Events']}")
    print(f"  Survival: {row['Survival_Rate_%']:.1f}% (CI: {row['CI_Low_%']:.1f}-{row['CI_High_%']:.1f}%)")
    print(f"  Lambda: {row['Lambda_Mean']:.3f} ± {row['Lambda_Std']:.3f}")

# ============================================================================
# FIGURE 1: Survival vs Lambda
# ============================================================================
print("\n" + "="*70)
print("GENERATING MECHANISM FIGURES")
print("="*70)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Survival probability vs lambda (binned)
ax = axes[0, 0]
if len(binned_df) > 0:
    x_pos = np.arange(len(binned_df))
    ax.bar(x_pos, binned_df['Survival_Rate_%'], color='steelblue', 
           alpha=0.7, edgecolor='black', linewidth=1.5)
    ax.errorbar(x_pos, binned_df['Survival_Rate_%'], 
                yerr=[binned_df['Survival_Rate_%'] - binned_df['CI_Low_%'],
                      binned_df['CI_High_%'] - binned_df['Survival_Rate_%']],
                fmt='none', ecolor='black', capsize=5, capthick=2)
    
    ax.set_xticks(x_pos)
    ax.set_xticklabels(binned_df['Lambda_Bin'], rotation=45, ha='right')
    ax.set_xlabel('Lambda (λ) Bin', fontsize=12, weight='bold')
    ax.set_ylabel('Survival Probability (%)', fontsize=12, weight='bold')
    ax.set_title('CE Survival vs Lambda', fontsize=14, weight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add sample sizes
    for i, (x, n) in enumerate(zip(x_pos, binned_df['N_Systems'])):
        ax.text(x, -5, f'n={n}', ha='center', fontsize=9)

# Plot 2: Lambda distributions by outcome
ax = axes[0, 1]
survived = all_ce[all_ce['survived_CE'] == True]
failed = all_ce[all_ce['survived_CE'] == False]

if len(survived) > 0 or len(failed) > 0:
    bins = np.linspace(0, 0.4, 20)
    if len(failed) > 0:
        ax.hist(failed['lambda_CE'], bins=bins, alpha=0.7, label=f'Failed CE (n={len(failed)})', 
                color='red', edgecolor='black')
    if len(survived) > 0:
        ax.hist(survived['lambda_CE'], bins=bins, alpha=0.7, label=f'Survived CE (n={len(survived)})', 
                color='green', edgecolor='black')
    
    ax.set_xlabel('Lambda (λ)', fontsize=12, weight='bold')
    ax.set_ylabel('Count', fontsize=12, weight='bold')
    ax.set_title('Lambda Distribution by Outcome', fontsize=14, weight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

# Plot 3: Survival by donor state
ax = axes[1, 0]
# Get top donor states
top_states = state_df.groupby('Donor_State')['N_CE_Events'].sum().nlargest(5).index

plot_data = state_df[state_df['Donor_State'].isin(top_states)]
if len(plot_data) > 0:
    x_pos = np.arange(len(plot_data))
    colors = plt.cm.Set3(np.linspace(0, 1, len(plot_data)))
    
    bars = ax.bar(x_pos, plot_data['Survival_Rate_%'], color=colors, 
                  alpha=0.7, edgecolor='black', linewidth=1.5)
    ax.errorbar(x_pos, plot_data['Survival_Rate_%'],
                yerr=[plot_data['Survival_Rate_%'] - plot_data['CI_Low_%'],
                      plot_data['CI_High_%'] - plot_data['Survival_Rate_%']],
                fmt='none', ecolor='black', capsize=5, capthick=2)
    
    ax.set_xticks(x_pos)
    labels = [f"{row['Donor_State']}\n{row['Metallicity']} Z\n(n={row['N_CE_Events']})" 
              for _, row in plot_data.iterrows()]
    ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=9)
    ax.set_ylabel('Survival Probability (%)', fontsize=12, weight='bold')
    ax.set_title('Survival by Donor Evolutionary State', fontsize=14, weight='bold')
    ax.grid(True, alpha=0.3, axis='y')

# Plot 4: Lambda by donor state (box plot)
ax = axes[1, 1]
if len(all_ce) > 0:
    # Get top states for plotting
    top_states_list = all_ce['donor_state'].value_counts().head(4).index.tolist()
    plot_ce = all_ce[all_ce['donor_state'].isin(top_states_list)]
    
    if len(plot_ce) > 0:
        # Create box plot
        positions = []
        data_to_plot = []
        labels = []
        
        for i, state in enumerate(top_states_list):
            state_data = plot_ce[plot_ce['donor_state'] == state]['lambda_CE'].dropna()
            if len(state_data) > 0:
                data_to_plot.append(state_data)
                positions.append(i)
                labels.append(f"{state}\n(n={len(state_data)})")
        
        bp = ax.boxplot(data_to_plot, positions=positions, widths=0.6,
                        patch_artist=True, showmeans=True)
        
        # Color boxes
        for patch in bp['boxes']:
            patch.set_facecolor('lightblue')
            patch.set_alpha(0.7)
        
        ax.set_xticks(positions)
        ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=10)
        ax.set_ylabel('Lambda (λ)', fontsize=12, weight='bold')
        ax.set_title('Lambda Distribution by Donor State', fontsize=14, weight='bold')
        ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(sensitivity_dir / 'survival_vs_lambda.png', dpi=300, bbox_inches='tight')
print(f"\n✓ Saved: {sensitivity_dir / 'survival_vs_lambda.png'}")

# ============================================================================
# ADDITIONAL FIGURE: Survival by State (Grouped by Metallicity)
# ============================================================================
print("\nGenerating survival by state figure...")

fig, ax = plt.subplots(figsize=(12, 6))

# Get unique states and metallicities
unique_states = state_df['Donor_State'].unique()
metallicities = ['Solar', 'Mid', 'Low']
colors_map = {'Solar': 'orange', 'Mid': 'blue', 'Low': 'purple'}

x = np.arange(len(unique_states))
width = 0.25

for i, met in enumerate(metallicities):
    met_data = state_df[state_df['Metallicity'] == met]
    survival_rates = []
    
    for state in unique_states:
        state_row = met_data[met_data['Donor_State'] == state]
        if len(state_row) > 0:
            survival_rates.append(state_row['Survival_Rate_%'].values[0])
        else:
            survival_rates.append(0)
    
    offset = (i - 1) * width
    ax.bar(x + offset, survival_rates, width, label=met, 
           color=colors_map[met], alpha=0.7, edgecolor='black', linewidth=1.5)

ax.set_xlabel('Donor Stellar State', fontsize=12, weight='bold')
ax.set_ylabel('Survival Probability (%)', fontsize=12, weight='bold')
ax.set_title('CE Survival by Evolutionary State and Metallicity', fontsize=14, weight='bold')
ax.set_xticks(x)
ax.set_xticklabels(unique_states, rotation=45, ha='right')
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(sensitivity_dir / 'survival_by_state.png', dpi=300, bbox_inches='tight')
print(f"✓ Saved: {sensitivity_dir / 'survival_by_state.png'}")

# ============================================================================
# SUMMARY STATISTICS
# ============================================================================
print("\n" + "="*70)
print("MECHANISM SUMMARY")
print("="*70)

print("\nKey findings:")
print(f"1. Lambda range: {all_ce['lambda_CE'].min():.3f} - {all_ce['lambda_CE'].max():.3f}")
print(f"2. Mean lambda: {all_ce['lambda_CE'].mean():.3f} ± {all_ce['lambda_CE'].std():.3f}")

# Find lambda threshold
if len(survived) > 0:
    lambda_crit_approx = survived['lambda_CE'].min()
    print(f"3. Minimum lambda for survival: {lambda_crit_approx:.3f}")
    print(f"   → Suggests λ_crit ≈ {lambda_crit_approx:.2f}")
else:
    print(f"3. No survivors in sample (all λ < some critical value)")

# State analysis
print("\n4. Survival by evolutionary phase:")
state_summary = state_df.groupby('Donor_State').agg({
    'N_CE_Events': 'sum',
    'N_Survived': 'sum',
    'Lambda_Mean': 'mean'
}).reset_index()
state_summary['Overall_Survival_%'] = state_summary['N_Survived'] / state_summary['N_CE_Events'] * 100

for _, row in state_summary.iterrows():
    print(f"   {row['Donor_State']}: {row['Overall_Survival_%']:.1f}% (λ̄={row['Lambda_Mean']:.3f})")

print("\n" + "="*70)
print("ANALYSIS COMPLETE")
print("="*70)
print("\nGenerated files:")
print(f"  • {sensitivity_dir / 'lambda_binned_survival.csv'}")
print(f"  • {sensitivity_dir / 'donor_state_stratified.csv'}")
print(f"  • {sensitivity_dir / 'survival_vs_lambda.png'}")
print(f"  • {sensitivity_dir / 'survival_by_state.png'}")
