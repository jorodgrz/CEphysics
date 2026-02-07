#!/usr/bin/env python3
"""
Debug script to inspect POSYDON binary history structure.

This script evolves a single binary and inspects the history DataFrame
to find where lambda_CE and other CE-related data are stored.
"""

import os
from pathlib import Path

# Set environment variables
os.environ['PATH_TO_POSYDON'] = str(Path.home() / "CEphysics/POSYDON")
os.environ['PATH_TO_POSYDON_DATA'] = str(Path.home() / "CEphysics/grids/POSYDON_data")

import shutil
from posydon.config import PATH_TO_POSYDON
from posydon.popsyn.io import simprop_kwargs_from_ini
from posydon.binary_evol.simulationproperties import SimulationProperties
from posydon.binary_evol.singlestar import SingleStar
from posydon.binary_evol.binarystar import BinaryStar
import warnings
warnings.filterwarnings('ignore')

print("="*70)
print("POSYDON BINARY HISTORY DEBUG SCRIPT")
print("="*70)

print("\nSetting up simulation properties...")
path_to_params = os.path.join(PATH_TO_POSYDON, "posydon/popsyn/population_params_default.ini")
shutil.copyfile(path_to_params, './population_params_debug.ini')

sim_kwargs = simprop_kwargs_from_ini('population_params_debug.ini')

# Set metallicity for MESA steps
metallicity_dict = {'metallicity': 1.0}  # Solar
mesa_steps = ['step_HMS_HMS', 'step_CO_HeMS', 'step_CO_HMS_RLO', 'step_CO_HeMS_RLO']

for step_name in mesa_steps:
    if step_name in sim_kwargs and len(sim_kwargs[step_name]) > 1:
        if isinstance(sim_kwargs[step_name][1], dict):
            sim_kwargs[step_name][1].update(metallicity_dict)

sim_prop = SimulationProperties(**sim_kwargs)

print("Loading POSYDON steps (this may take 2-3 minutes)...")
sim_prop.load_steps(verbose=False)
print("✓ Steps loaded!\n")

print("Creating binary system...")
print("  Using parameters from your CE survivor:")
print("  M1 = 20.0 M☉, M2 = 9.33 M☉, P = 500 days")

# Use the survivor parameters from your results!
star1 = SingleStar(mass=20.0, state='H-rich_Core_H_burning')
star2 = SingleStar(mass=9.333333, state='H-rich_Core_H_burning')

binary = BinaryStar(
    star1, star2,
    time=0.0,
    state='detached',
    event='ZAMS',
    orbital_period=500.0,
    eccentricity=0.0,
    properties=sim_prop
)

print("\nEvolving binary (this may take 10-30 seconds)...")
binary.evolve()
print("✓ Evolution complete!\n")

print("="*70)
print("INSPECTING BINARY OBJECT")
print("="*70)

# Check what attributes exist
print("\nBinary top-level attributes:")
attrs = [attr for attr in dir(binary) if not attr.startswith('_')]
print(attrs[:20])  # Show first 20
print(f"... and {len(attrs) - 20} more")

# Try to get history
print("\n" + "="*70)
print("CHECKING HISTORY METHODS")
print("="*70)

if hasattr(binary, 'to_df'):
    print("\n✓ binary.to_df() method exists!")
    hist = binary.to_df()
    print(f"\nHistory DataFrame shape: {hist.shape} (rows × columns)")
    
    print("\n" + "-"*70)
    print("ALL COLUMN NAMES:")
    print("-"*70)
    for i, col in enumerate(hist.columns, 1):
        print(f"{i:3d}. {col}")
    
    print("\n" + "-"*70)
    print("SEARCHING FOR CE-RELATED COLUMNS:")
    print("-"*70)
    ce_cols = [col for col in hist.columns if 'CE' in col or 'lambda' in col.lower() or 'envelope' in col.lower()]
    if ce_cols:
        print(f"✓ Found {len(ce_cols)} CE-related columns:")
        for col in ce_cols:
            print(f"  - {col}")
    else:
        print("✗ No obvious CE-related columns found")
    
    print("\n" + "-"*70)
    print("EVENT COLUMN ANALYSIS:")
    print("-"*70)
    if 'event' in hist.columns:
        print("\n✓ 'event' column exists!")
        print("\nAll unique events in this binary's history:")
        for i, event in enumerate(hist['event'].unique(), 1):
            count = (hist['event'] == event).sum()
            print(f"  {i:2d}. {event:30s} (occurred {count} times)")
        
        # Check CE events specifically
        ce_rows = hist[hist['event'].str.contains('CE', na=False)]
        if len(ce_rows) > 0:
            print(f"\n{'='*70}")
            print(f"✓✓✓ FOUND {len(ce_rows)} CE EVENT(S)! ✓✓✓")
            print("="*70)
            print("\nCE event row(s) - ALL COLUMNS:")
            print(ce_rows.to_string())
            
            print("\n" + "-"*70)
            print("CE EVENT SPECIFIC DATA:")
            print("-"*70)
            for idx, row in ce_rows.iterrows():
                print(f"\nCE Event at index {idx}:")
                print(f"  Time: {row.get('time', 'N/A')} years")
                print(f"  State: {row.get('state', 'N/A')}")
                print(f"  Star 1 state: {row.get('star_1_state', 'N/A')}")
                print(f"  Star 2 state: {row.get('star_2_state', 'N/A')}")
                print(f"  Orbital period: {row.get('orbital_period', 'N/A')} days")
                
                # Try various lambda column names
                lambda_candidates = ['lambda_CE', 'lambda_CE_1Msun', 'lambda_CE_10Msun', 
                                   'CE_lambda', 'lambda', 'lambda_1', 'lambda_2']
                print("\n  Lambda search:")
                for lam_col in lambda_candidates:
                    if lam_col in row.index:
                        print(f"    ✓ {lam_col}: {row[lam_col]}")
        else:
            print("\n✗ No CE events found in this binary's history")
            print("   (The binary may have evolved differently than expected)")
    else:
        print("✗ No 'event' column found")
        
    print("\n" + "-"*70)
    print("FIRST 5 ROWS OF HISTORY (ALL COLUMNS):")
    print("-"*70)
    print(hist.head().to_string())
    
    print("\n" + "-"*70)
    print("LAST 5 ROWS OF HISTORY (ALL COLUMNS):")
    print("-"*70)
    print(hist.tail().to_string())
    
else:
    print("\n✗ No to_df() method found")
    print("\nTrying alternative history access methods...")
    
    if hasattr(binary, 'history'):
        print("✓ binary.history exists")
        print("  Type:", type(binary.history))
        print("  Attributes:", [a for a in dir(binary.history) if not a.startswith('_')])
    else:
        print("✗ No binary.history attribute")

print("\n" + "="*70)
print("DEBUG COMPLETE")
print("="*70)
print("\nNext steps:")
print("1. Look for the columns that contain lambda values")
print("2. Note the exact column names")
print("3. Update extract_CE_data() in run_population.py with correct column names")
print("4. Re-run your population synthesis")
