#!/usr/bin/env python3
"""
Test evolving a single binary system with POSYDON.

This is a quick test to ensure the full evolution pipeline works.

Usage:
    conda activate posydon
    python test_single_binary.py
"""

import os
import sys
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set POSYDON paths
POSYDON_PATH = Path(__file__).parent / "POSYDON"
POSYDON_DATA_PATH = Path(__file__).parent / "grids" / "POSYDON_data"
os.environ['PATH_TO_POSYDON'] = str(POSYDON_PATH)
os.environ['PATH_TO_POSYDON_DATA'] = str(POSYDON_DATA_PATH)

print("="*60)
print("SINGLE BINARY EVOLUTION TEST")
print("="*60)
print()

# Import POSYDON
print("Importing POSYDON modules...")
try:
    import posydon
    from posydon.popsyn.io import simprop_kwargs_from_ini
    from posydon.binary_evol.simulationproperties import SimulationProperties
    from posydon.binary_evol.singlestar import SingleStar
    from posydon.binary_evol.binarystar import BinaryStar
    from posydon.config import PATH_TO_POSYDON
    import shutil
    print(f"✓ POSYDON v{posydon.__version__} imported\n")
except ImportError as e:
    print(f"✗ Failed to import POSYDON: {e}")
    sys.exit(1)

# Define test binary
print("Test Binary Parameters:")
M1 = 12.0  # Solar masses
M2 = 10.0  # Solar masses
P_orb = 500.0  # days
Z = 0.014  # Solar metallicity

print(f"  Primary Mass (M1): {M1} M☉")
print(f"  Secondary Mass (M2): {M2} M☉")
print(f"  Orbital Period (P): {P_orb} days")
print(f"  Metallicity (Z): {Z} (solar)")
print(f"  Eccentricity: 0.0 (circular)")
print()

# Configure simulation
print("Configuring simulation properties...")
try:
    # Copy default population params
    path_to_params = os.path.join(PATH_TO_POSYDON, "posydon/popsyn/population_params_default.ini")
    shutil.copyfile(path_to_params, './population_params_test.ini')
    
    # Load simulation properties from ini file
    sim_kwargs = simprop_kwargs_from_ini('population_params_test.ini')
    
    # Set metallicity for all steps
    metallicity_dict = {'metallicity': Z / 0.014}  # Normalized to solar
    
    for step_name in sim_kwargs.keys():
        if step_name.startswith('step_'):
            if len(sim_kwargs[step_name]) > 1 and isinstance(sim_kwargs[step_name][1], dict):
                sim_kwargs[step_name][1].update(metallicity_dict)
    
    sim_prop = SimulationProperties(**sim_kwargs)
    
    # Load the steps and required data
    print("Loading POSYDON steps and data (this may take a moment)...")
    sim_prop.load_steps(verbose=False)
    
    print("✓ Simulation properties configured\n")
except Exception as e:
    print(f"✗ Failed to configure simulation: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Evolve binary
print("="*60)
print("EVOLVING BINARY...")
print("="*60)
print("This may take a few minutes...\n")

try:
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
    print("Starting evolution...")
    binary.evolve()
    
    print("✓ Evolution complete!\n")
    print("="*60)
    print("RESULTS")
    print("="*60)
    
    # Print final state
    print(f"\nFinal State: {binary.state}")
    
    # Print history summary
    if hasattr(binary, 'history'):
        history = binary.history
        print(f"\nEvolution History:")
        print(f"  Number of steps: {len(history)}")
        
        # Check for CE event
        if hasattr(history, 'step_names'):
            step_names = [str(s) for s in history.step_names]
            ce_events = [i for i, s in enumerate(step_names) if 'step_CE' in s or 'CE' in s]
            
            if ce_events:
                print(f"  Common Envelope events: {len(ce_events)}")
                for i, ce_idx in enumerate(ce_events):
                    print(f"\n  CE Event #{i+1} at step {ce_idx}:")
                    print(f"    Step name: {step_names[ce_idx]}")
                    
                    # Try to extract lambda if available
                    if hasattr(history, 'lambda_CE_1Msun'):
                        try:
                            lambda_val = history.lambda_CE_1Msun[ce_idx]
                            if lambda_val is not None and not (hasattr(lambda_val, '__iter__') and len(lambda_val) == 0):
                                print(f"    λ_CE: {lambda_val}")
                        except:
                            pass
            else:
                print("  No Common Envelope events detected")
        
        # Print final binary properties
        print(f"\nFinal Binary Properties:")
        if hasattr(history, 'star_1_mass'):
            print(f"  Star 1 mass: {history.star_1_mass[-1]:.2f} M☉")
        if hasattr(history, 'star_2_mass'):
            print(f"  Star 2 mass: {history.star_2_mass[-1]:.2f} M☉")
        if hasattr(history, 'period_days'):
            print(f"  Orbital period: {history.period_days[-1]:.2f} days")
        if hasattr(history, 'eccentricity'):
            print(f"  Eccentricity: {history.eccentricity[-1]:.4f}")
    
    print("\n" + "="*60)
    print("✅ BINARY EVOLUTION TEST SUCCESSFUL!")
    print("="*60)
    print("\nYou're ready to run your full population synthesis!")
    print("\nNext steps:")
    print("1. jupyter notebook CE_research_project.ipynb")
    print("2. or: python run_population.py --n_systems 10 --output test.h5")
    print("="*60)
    
except Exception as e:
    print(f"\n✗ Evolution failed: {e}")
    print(f"\nError type: {type(e).__name__}")
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()
    print("\n" + "="*60)
    print("If you see errors about missing grids or data files,")
    print("you may need to download additional metallicity grids.")
    print("="*60)
    sys.exit(1)
