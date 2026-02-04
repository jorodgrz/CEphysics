#!/usr/bin/env python3
"""
Run POSYDON population synthesis for CE research project.

This script can be run from the command line for batch processing.
Usage:
    conda activate posydon
    python run_population.py --metallicity 0.014 --n_systems 100 --output results.h5
"""

import argparse
import numpy as np
import pandas as pd
from pathlib import Path
from tqdm import tqdm
import posydon
from posydon.binary_evol.simulationproperties import SimulationProperties
from posydon.binary_evol.binarystar import BinaryStar
from posydon.binary_evol.flow_chart import flow_chart
import warnings
warnings.filterwarnings('ignore')


def create_binary_grid(M1_range, M2_range, P_range, metallicities, n_samples=None):
    """
    Create grid of binary initial conditions.
    
    Parameters:
    -----------
    M1_range : tuple
        (min, max, n_samples) for primary mass
    M2_range : tuple
        (min, max, n_samples) for secondary mass
    P_range : tuple
        (min, max, n_samples) for orbital period
    metallicities : list
        List of metallicity values
    n_samples : int, optional
        If provided, randomly sample this many systems instead of full grid
    
    Returns:
    --------
    DataFrame with initial conditions
    """
    # Generate grids
    M1_grid = np.linspace(*M1_range)
    M2_grid = np.linspace(*M2_range)
    P_grid = np.logspace(np.log10(P_range[0]), np.log10(P_range[1]), P_range[2])
    
    binary_list = []
    
    for Z in metallicities:
        for M1 in M1_grid:
            for M2 in M2_grid:
                if M1 >= M2:  # Primary more massive
                    for P in P_grid:
                        binary_list.append({
                            'M1': M1,
                            'M2': M2,
                            'P_orb': P,
                            'Z': Z,
                            'q': M2/M1,
                        })
    
    df = pd.DataFrame(binary_list)
    
    # Random sampling if requested
    if n_samples and n_samples < len(df):
        df = df.sample(n=n_samples, random_state=42)
    
    return df


def setup_simulation_properties(metallicity=0.014, alpha_CE=1.0):
    """
    Configure POSYDON simulation properties.
    """
    sim_prop = SimulationProperties(
        flow_chart=flow_chart,
        common_envelope_alpha_thermal=alpha_CE,
        common_envelope_option_for_lambda='lambda_from_grid_final_values',
        common_envelope_lambda_default=0.5,
        metallicity=metallicity,
        max_simulation_time=13.8e9,
    )
    return sim_prop


def evolve_binary(M1, M2, P_orb, Z, sim_prop):
    """
    Evolve a single binary system.
    """
    sim_prop.metallicity = Z
    
    binary = BinaryStar.from_run(
        m1=M1,
        m2=M2,
        period_days=P_orb,
        eccentricity=0.0,
        **sim_prop.__dict__
    )
    
    return binary


def extract_CE_data(binary, initial_conditions):
    """
    Extract CE event data from evolved binary.
    """
    ce_data = {
        'M1_initial': initial_conditions['M1'],
        'M2_initial': initial_conditions['M2'],
        'P_initial': initial_conditions['P_orb'],
        'Z': initial_conditions['Z'],
        'q_initial': initial_conditions['q'],
        'CE_occurred': False,
        'lambda_CE': np.nan,
        'donor_state': None,
        'survived_CE': False,
        'final_state': str(binary.state) if hasattr(binary, 'state') else None,
    }
    
    # Check binary history for CE events
    # This is a placeholder - actual implementation depends on POSYDON output structure
    try:
        history = binary.history
        
        # Look for CE step in history
        if hasattr(history, 'step_names'):
            ce_steps = [i for i, step in enumerate(history.step_names) 
                       if 'step_CE' in str(step)]
            
            if ce_steps:
                ce_data['CE_occurred'] = True
                ce_idx = ce_steps[0]
                
                # Extract lambda if available
                if hasattr(history, 'lambda_CE_1Msun'):
                    ce_data['lambda_CE'] = history.lambda_CE_1Msun[ce_idx]
                
                # Extract donor state
                if hasattr(history, 'star_1_state'):
                    ce_data['donor_state'] = str(history.star_1_state[ce_idx])
                
                # Check if survived
                ce_data['survived_CE'] = binary.state not in ['merged', 'initial_RLOF']
        
    except Exception as e:
        print(f"Warning: Could not extract CE data: {e}")
    
    return ce_data


def run_population(binary_grid, output_file, alpha_CE=1.0, verbose=True):
    """
    Run population synthesis on binary grid.
    
    Parameters:
    -----------
    binary_grid : DataFrame
        Initial conditions
    output_file : str
        Output HDF5 file path
    alpha_CE : float
        Common envelope efficiency parameter
    verbose : bool
        Print progress
    """
    results = []
    sim_prop = setup_simulation_properties(alpha_CE=alpha_CE)
    
    iterator = tqdm(binary_grid.iterrows(), total=len(binary_grid)) if verbose else binary_grid.iterrows()
    
    for idx, row in iterator:
        try:
            # Evolve binary
            binary = evolve_binary(
                M1=row['M1'],
                M2=row['M2'],
                P_orb=row['P_orb'],
                Z=row['Z'],
                sim_prop=sim_prop
            )
            
            # Extract data
            ce_data = extract_CE_data(binary, row)
            results.append(ce_data)
            
        except Exception as e:
            if verbose:
                print(f"\nError at index {idx}: {e}")
            results.append({
                'M1_initial': row['M1'],
                'M2_initial': row['M2'],
                'P_initial': row['P_orb'],
                'Z': row['Z'],
                'error': str(e)
            })
    
    # Save results
    results_df = pd.DataFrame(results)
    results_df.to_hdf(output_file, key='results', mode='w')
    
    if verbose:
        print(f"\nResults saved to {output_file}")
        print(f"Total systems evolved: {len(results_df)}")
        print(f"Systems with CE events: {results_df['CE_occurred'].sum()}")
        if results_df['CE_occurred'].sum() > 0:
            print(f"CE survival rate: {results_df[results_df['CE_occurred']]['survived_CE'].mean():.2%}")
    
    return results_df


def main():
    parser = argparse.ArgumentParser(
        description='Run POSYDON population synthesis for CE research'
    )
    parser.add_argument('--metallicity', type=float, nargs='+', 
                       default=[0.014],
                       help='Metallicity values (default: 0.014)')
    parser.add_argument('--M1_min', type=float, default=8.0,
                       help='Minimum primary mass (default: 8.0)')
    parser.add_argument('--M1_max', type=float, default=20.0,
                       help='Maximum primary mass (default: 20.0)')
    parser.add_argument('--M1_samples', type=int, default=10,
                       help='Number of M1 samples (default: 10)')
    parser.add_argument('--M2_min', type=float, default=8.0,
                       help='Minimum secondary mass (default: 8.0)')
    parser.add_argument('--M2_max', type=float, default=20.0,
                       help='Maximum secondary mass (default: 20.0)')
    parser.add_argument('--M2_samples', type=int, default=10,
                       help='Number of M2 samples (default: 10)')
    parser.add_argument('--P_min', type=float, default=100,
                       help='Minimum period in days (default: 100)')
    parser.add_argument('--P_max', type=float, default=5000,
                       help='Maximum period in days (default: 5000)')
    parser.add_argument('--P_samples', type=int, default=10,
                       help='Number of period samples (default: 10)')
    parser.add_argument('--n_systems', type=int, default=None,
                       help='Randomly sample this many systems (default: all)')
    parser.add_argument('--alpha_CE', type=float, default=1.0,
                       help='CE efficiency parameter (default: 1.0)')
    parser.add_argument('--output', type=str, default='CE_results.h5',
                       help='Output HDF5 file (default: CE_results.h5)')
    parser.add_argument('--quiet', action='store_true',
                       help='Suppress progress output')
    
    args = parser.parse_args()
    
    # Print configuration
    if not args.quiet:
        print("="*60)
        print("POSYDON CE Population Synthesis")
        print(f"Version: {posydon.__version__}")
        print("="*60)
        print(f"\nParameters:")
        print(f"  M1: {args.M1_min} - {args.M1_max} M☉ ({args.M1_samples} samples)")
        print(f"  M2: {args.M2_min} - {args.M2_max} M☉ ({args.M2_samples} samples)")
        print(f"  P: {args.P_min} - {args.P_max} days ({args.P_samples} samples)")
        print(f"  Metallicities: {args.metallicity}")
        print(f"  CE efficiency α: {args.alpha_CE}")
        print(f"  Output file: {args.output}")
        print()
    
    # Create binary grid
    binary_grid = create_binary_grid(
        M1_range=(args.M1_min, args.M1_max, args.M1_samples),
        M2_range=(args.M2_min, args.M2_max, args.M2_samples),
        P_range=(args.P_min, args.P_max, args.P_samples),
        metallicities=args.metallicity,
        n_samples=args.n_systems
    )
    
    if not args.quiet:
        print(f"Created grid with {len(binary_grid)} binary systems\n")
    
    # Run population synthesis
    results_df = run_population(
        binary_grid, 
        args.output, 
        alpha_CE=args.alpha_CE,
        verbose=not args.quiet
    )
    
    if not args.quiet:
        print("\n" + "="*60)
        print("Population synthesis complete!")
        print("="*60)


if __name__ == '__main__':
    main()
