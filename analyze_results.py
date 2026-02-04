#!/usr/bin/env python3
"""
Analyze POSYDON population synthesis results for CE research.

Usage:
    python analyze_results.py --input CE_results.h5 --output-dir analysis_plots/
"""

import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from pathlib import Path
import seaborn as sns

# Configure plotting style
plt.style.use('seaborn-v0_8-darkgrid')
mpl.rcParams['figure.figsize'] = (12, 8)
mpl.rcParams['font.size'] = 11


def load_results(filename):
    """Load results from HDF5 file."""
    print(f"Loading results from {filename}...")
    df = pd.read_hdf(filename, key='results')
    print(f"Loaded {len(df)} systems")
    return df


def basic_statistics(df):
    """Print basic statistics about the population."""
    print("\n" + "="*60)
    print("POPULATION STATISTICS")
    print("="*60)
    
    print(f"\nTotal systems: {len(df)}")
    
    if 'CE_occurred' in df.columns:
        ce_systems = df[df['CE_occurred'] == True]
        print(f"Systems with CE events: {len(ce_systems)} ({100*len(ce_systems)/len(df):.1f}%)")
        
        if len(ce_systems) > 0 and 'survived_CE' in ce_systems.columns:
            survived = ce_systems['survived_CE'].sum()
            print(f"Systems that survived CE: {survived} ({100*survived/len(ce_systems):.1f}%)")
            
            # Statistics by metallicity
            if 'Z' in df.columns:
                print("\nBy Metallicity:")
                for Z in sorted(df['Z'].unique()):
                    z_systems = ce_systems[ce_systems['Z'] == Z]
                    if len(z_systems) > 0:
                        survival_rate = z_systems['survived_CE'].mean()
                        print(f"  Z = {Z:.4f}: {len(z_systems)} CE events, "
                              f"{100*survival_rate:.1f}% survival")
    
    print("="*60 + "\n")


def plot_lambda_distribution(df, output_dir):
    """Plot binding energy parameter distributions."""
    ce_systems = df[df['CE_occurred'] == True]
    
    if 'lambda_CE' not in ce_systems.columns or ce_systems['lambda_CE'].isna().all():
        print("Warning: No lambda_CE data available")
        return
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Overall distribution
    ax = axes[0]
    ce_systems['lambda_CE'].dropna().hist(bins=50, ax=ax, edgecolor='black', alpha=0.7)
    ax.axvline(0.1, color='red', linestyle='--', linewidth=2, label='Fixed λ = 0.1')
    ax.axvline(0.5, color='orange', linestyle='--', linewidth=2, label='Fixed λ = 0.5')
    ax.set_xlabel('$\\lambda_{\\mathrm{env}}$', fontsize=14)
    ax.set_ylabel('Number of Systems', fontsize=14)
    ax.set_title('Binding Energy Parameter Distribution', fontsize=15)
    ax.legend(fontsize=12)
    ax.grid(True, alpha=0.3)
    
    # By metallicity
    ax = axes[1]
    if 'Z' in ce_systems.columns:
        for Z in sorted(ce_systems['Z'].unique()):
            subset = ce_systems[ce_systems['Z'] == Z]
            if len(subset) > 0:
                subset['lambda_CE'].dropna().hist(bins=30, ax=ax, alpha=0.5, 
                                                  label=f'Z = {Z:.4f}')
        ax.set_xlabel('$\\lambda_{\\mathrm{env}}$', fontsize=14)
        ax.set_ylabel('Number of Systems', fontsize=14)
        ax.set_title('Lambda Distribution by Metallicity', fontsize=15)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/lambda_distribution.png', dpi=150, bbox_inches='tight')
    print(f"Saved: {output_dir}/lambda_distribution.png")
    plt.close()


def plot_metallicity_effects(df, output_dir):
    """Plot metallicity dependence of CE outcomes."""
    ce_systems = df[df['CE_occurred'] == True]
    
    if 'Z' not in ce_systems.columns:
        print("Warning: No metallicity data available")
        return
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Survival rate vs metallicity
    ax = axes[0]
    survival_by_Z = ce_systems.groupby('Z')['survived_CE'].agg(['mean', 'count'])
    
    ax.plot(survival_by_Z.index, survival_by_Z['mean'], 'o-', 
            linewidth=2, markersize=10, color='steelblue')
    ax.set_xlabel('Metallicity Z', fontsize=14)
    ax.set_ylabel('CE Survival Fraction', fontsize=14)
    ax.set_xscale('log')
    ax.set_title('Does Low Z Create a \"Death Trap\"?', fontsize=15)
    ax.grid(True, alpha=0.3)
    ax.set_ylim([0, 1])
    
    # Add sample sizes
    for Z, row in survival_by_Z.iterrows():
        ax.annotate(f'n={int(row["count"])}', 
                   xy=(Z, row['mean']), 
                   xytext=(0, 10), textcoords='offset points',
                   ha='center', fontsize=9, alpha=0.7)
    
    # Average lambda vs metallicity
    ax = axes[1]
    if 'lambda_CE' in ce_systems.columns:
        lambda_by_Z = ce_systems.groupby('Z')['lambda_CE'].agg(['mean', 'std'])
        
        ax.errorbar(lambda_by_Z.index, lambda_by_Z['mean'], 
                   yerr=lambda_by_Z['std'], fmt='s-', 
                   linewidth=2, markersize=10, capsize=5, color='coral')
        ax.set_xlabel('Metallicity Z', fontsize=14)
        ax.set_ylabel('Mean $\\lambda_{\\mathrm{env}}$', fontsize=14)
        ax.set_xscale('log')
        ax.set_title('Binding Energy vs Metallicity', fontsize=15)
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/metallicity_effects.png', dpi=150, bbox_inches='tight')
    print(f"Saved: {output_dir}/metallicity_effects.png")
    plt.close()


def plot_mass_period_space(df, output_dir):
    """Plot outcomes in mass-period parameter space."""
    ce_systems = df[df['CE_occurred'] == True]
    
    if len(ce_systems) == 0:
        print("Warning: No CE events to plot")
        return
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # M1 vs M2, colored by survival
    ax = axes[0]
    if 'survived_CE' in ce_systems.columns:
        survived = ce_systems[ce_systems['survived_CE'] == True]
        merged = ce_systems[ce_systems['survived_CE'] == False]
        
        ax.scatter(merged['M1_initial'], merged['M2_initial'], 
                  c='red', alpha=0.6, s=50, label='Merged', marker='x')
        ax.scatter(survived['M1_initial'], survived['M2_initial'], 
                  c='green', alpha=0.6, s=50, label='Survived', marker='o')
    else:
        ax.scatter(ce_systems['M1_initial'], ce_systems['M2_initial'], 
                  alpha=0.6, s=50)
    
    ax.plot([8, 20], [8, 20], 'k--', alpha=0.3, label='M1 = M2')
    ax.set_xlabel('Primary Mass $M_1$ [$M_{\odot}$]', fontsize=14)
    ax.set_ylabel('Secondary Mass $M_2$ [$M_{\odot}$]', fontsize=14)
    ax.set_title('CE Outcomes in Mass Space', fontsize=15)
    ax.legend(fontsize=12)
    ax.grid(True, alpha=0.3)
    
    # M1 vs Period, colored by lambda
    ax = axes[1]
    if 'lambda_CE' in ce_systems.columns:
        scatter = ax.scatter(ce_systems['M1_initial'], ce_systems['P_initial'], 
                           c=ce_systems['lambda_CE'], cmap='viridis', 
                           alpha=0.7, s=50, edgecolors='black', linewidth=0.5)
        plt.colorbar(scatter, ax=ax, label='$\\lambda_{\\mathrm{env}}$')
    else:
        ax.scatter(ce_systems['M1_initial'], ce_systems['P_initial'], 
                  alpha=0.7, s=50)
    
    ax.set_xlabel('Primary Mass $M_1$ [$M_{\odot}$]', fontsize=14)
    ax.set_ylabel('Initial Period [days]', fontsize=14)
    ax.set_yscale('log')
    ax.set_title('Lambda Distribution in Parameter Space', fontsize=15)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/parameter_space.png', dpi=150, bbox_inches='tight')
    print(f"Saved: {output_dir}/parameter_space.png")
    plt.close()


def export_summary_table(df, output_dir):
    """Export summary statistics as CSV."""
    ce_systems = df[df['CE_occurred'] == True]
    
    if len(ce_systems) == 0:
        print("Warning: No CE events to summarize")
        return
    
    # Overall summary
    summary = {
        'Total Systems': len(df),
        'CE Events': len(ce_systems),
        'CE Fraction': len(ce_systems) / len(df),
    }
    
    if 'survived_CE' in ce_systems.columns:
        summary['Survived CE'] = ce_systems['survived_CE'].sum()
        summary['Survival Rate'] = ce_systems['survived_CE'].mean()
    
    pd.DataFrame([summary]).to_csv(f'{output_dir}/overall_summary.csv', index=False)
    print(f"Saved: {output_dir}/overall_summary.csv")
    
    # Summary by metallicity
    if 'Z' in ce_systems.columns:
        z_summary = ce_systems.groupby('Z').agg({
            'survived_CE': ['count', 'sum', 'mean'],
            'lambda_CE': ['mean', 'std', 'min', 'max'] if 'lambda_CE' in ce_systems.columns else ['count']
        })
        z_summary.to_csv(f'{output_dir}/summary_by_metallicity.csv')
        print(f"Saved: {output_dir}/summary_by_metallicity.csv")


def main():
    parser = argparse.ArgumentParser(
        description='Analyze POSYDON CE population synthesis results'
    )
    parser.add_argument('--input', type=str, required=True,
                       help='Input HDF5 file with results')
    parser.add_argument('--output-dir', type=str, default='analysis',
                       help='Output directory for plots and tables (default: analysis)')
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    print("="*60)
    print("CE POPULATION ANALYSIS")
    print("="*60)
    print(f"Input file: {args.input}")
    print(f"Output directory: {output_dir}")
    print()
    
    # Load results
    df = load_results(args.input)
    
    # Print statistics
    basic_statistics(df)
    
    # Generate plots
    print("Generating plots...")
    plot_lambda_distribution(df, output_dir)
    plot_metallicity_effects(df, output_dir)
    plot_mass_period_space(df, output_dir)
    
    # Export tables
    print("\nExporting summary tables...")
    export_summary_table(df, output_dir)
    
    print("\n" + "="*60)
    print("Analysis complete!")
    print(f"Results saved to: {output_dir}/")
    print("="*60)


if __name__ == '__main__':
    main()
