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
import os
import shutil
import posydon
from posydon.config import PATH_TO_POSYDON
from posydon.popsyn.io import simprop_kwargs_from_ini
from posydon.binary_evol.simulationproperties import SimulationProperties
from posydon.binary_evol.singlestar import SingleStar
from posydon.binary_evol.binarystar import BinaryStar
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
    Configure POSYDON simulation properties using ini file.
    """
    # Copy default population params
    path_to_params = os.path.join(PATH_TO_POSYDON, "posydon/popsyn/population_params_default.ini")
    
    # Create local copy if it doesn't exist
    if not os.path.exists('./population_params.ini'):
        shutil.copyfile(path_to_params, './population_params.ini')
    
    # Load simulation properties from ini file
    sim_kwargs = simprop_kwargs_from_ini('population_params.ini')
    
    # Set metallicity for MESA grid steps (normalized to solar)
    metallicity_dict = {'metallicity': metallicity / 0.014}
    
    # Only add to steps that use MESA grids
    mesa_steps = ['step_HMS_HMS', 'step_CO_HeMS', 'step_CO_HMS_RLO', 'step_CO_HeMS_RLO']
    
    for step_name in mesa_steps:
        if step_name in sim_kwargs and len(sim_kwargs[step_name]) > 1:
            if isinstance(sim_kwargs[step_name][1], dict):
                sim_kwargs[step_name][1].update(metallicity_dict)
    
    # Create simulation properties
    sim_prop = SimulationProperties(**sim_kwargs)
    
    return sim_prop


def evolve_binary(M1, M2, P_orb, Z, sim_prop):
    """
    Evolve a single binary system using correct POSYDON API.
    """
    # Create single stars
    star1 = SingleStar(mass=M1, state='H-rich_Core_H_burning')
    star2 = SingleStar(mass=M2, state='H-rich_Core_H_burning')
    
    # Create binary
    binary = BinaryStar(
        star1, star2,
        time=0.0,
        state='detached',
        event='ZAMS',
        orbital_period=P_orb,
        eccentricity=0.0,
        properties=sim_prop
    )
    
    # Evolve the binary
    binary.evolve()
    
    return binary


def extract_CE_data(binary, initial_conditions):
    """
    Extract CE event data from evolved binary using POSYDON history DataFrame.
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
        'final_M1': np.nan,
        'final_M2': np.nan,
        'final_P': np.nan,
    }
    
    # Extract final state information
    try:
        if hasattr(binary, 'star_1') and hasattr(binary.star_1, 'mass'):
            ce_data['final_M1'] = binary.star_1.mass
        if hasattr(binary, 'star_2') and hasattr(binary.star_2, 'mass'):
            ce_data['final_M2'] = binary.star_2.mass
        if hasattr(binary, 'orbital_period'):
            ce_data['final_P'] = binary.orbital_period
    except:
        pass
    
    # Check for CE events in the binary's event history
    try:
        # POSYDON stores history as a pandas DataFrame accessible via to_df()
        if hasattr(binary, 'to_df'):
            history_df = binary.to_df()
            
            # Look for CE events in the 'event' column
            if 'event' in history_df.columns:
                ce_events = history_df[history_df['event'].str.contains('CE', na=False)]
                
                if len(ce_events) > 0:
                    ce_data['CE_occurred'] = True
                    
                    # Get first CE event
                    ce_row = ce_events.iloc[0]
                    
                    # Extract lambda if available
                    if 'lambda_CE_1Msun' in history_df.columns:
                        ce_data['lambda_CE'] = ce_row.get('lambda_CE_1Msun', np.nan)
                    
                    # Extract donor state before CE
                    if 'star_1_state' in history_df.columns:
                        ce_data['donor_state'] = str(ce_row.get('star_1_state', 'unknown'))
                    
                    # Check if system survived CE
                    ce_data['survived_CE'] = binary.state not in ['merged', 'initial_RLOF', 'disrupted']
        
    except Exception as e:
        # Silently fail - not all binaries will have CE events
        pass
    
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
    
    # Setup simulation properties (do this once)
    if verbose:
        print("Loading simulation properties and POSYDON grids...")
        print("(This takes 2-5 minutes on first run)\n")
    
    sim_prop = setup_simulation_properties(alpha_CE=alpha_CE)
    
    # Load steps once (not per binary!)
    if verbose:
        print("Loading POSYDON steps...")
    sim_prop.load_steps(verbose=verbose)
    if verbose:
        print("✅ Steps loaded! Starting evolution...\n")
    
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
        
        # Check if CE_occurred column exists and has data
        if 'CE_occurred' in results_df.columns:
            # Use == True to handle NaN values properly
            ce_systems = results_df[results_df['CE_occurred'] == True]
            ce_count = len(ce_systems)
            print(f"Systems with CE events: {ce_count}")
            if ce_count > 0 and 'survived_CE' in results_df.columns:
                # Filter out NaN values in survived_CE
                valid_survival = ce_systems['survived_CE'].dropna()
                if len(valid_survival) > 0:
                    print(f"CE survival rate: {valid_survival.mean():.2%}")
                else:
                    print(f"CE survival rate: N/A (no survival data)")
        
        # Check for errors
        if 'error' in results_df.columns:
            error_count = results_df['error'].notna().sum()
            if error_count > 0:
                print(f"⚠ Systems with errors: {error_count}")
                print(f"  Sample error: {results_df[results_df['error'].notna()]['error'].iloc[0]}")
    
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
