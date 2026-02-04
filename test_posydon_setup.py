#!/usr/bin/env python3
"""
Test POSYDON setup and verify data grids are accessible.

Usage:
    conda activate posydon
    python test_posydon_setup.py
"""

import os
import sys
from pathlib import Path

# Set POSYDON data path
POSYDON_DATA_PATH = Path(__file__).parent / "grids" / "POSYDON_data"
os.environ['PATH_TO_POSYDON_DATA'] = str(POSYDON_DATA_PATH)

print("="*60)
print("POSYDON SETUP TEST")
print("="*60)
print()

# Test 1: Check POSYDON import
print("Test 1: Importing POSYDON...")
try:
    import posydon
    print(f"✓ POSYDON imported successfully (v{posydon.__version__})")
except ImportError as e:
    print(f"✗ Failed to import POSYDON: {e}")
    sys.exit(1)

# Test 2: Check data path
print("\nTest 2: Checking data path...")
print(f"PATH_TO_POSYDON_DATA = {POSYDON_DATA_PATH}")
if POSYDON_DATA_PATH.exists():
    print(f"✓ Data directory exists")
else:
    print(f"✗ Data directory not found!")
    sys.exit(1)

# Test 3: Check for key grid files
print("\nTest 3: Checking for grid files...")
expected_grids = [
    "HMS-HMS_RLO/1e+00_Zsun.h5",
    "CO-HeMS_RLO/1e+00_Zsun.h5",
    "single_HMS/1e+00_Zsun.h5",
]

all_found = True
for grid in expected_grids:
    grid_path = POSYDON_DATA_PATH / grid
    if grid_path.exists():
        size_mb = grid_path.stat().st_size / 1e6
        print(f"✓ Found {grid} ({size_mb:.1f} MB)")
    else:
        print(f"✗ Missing {grid}")
        all_found = False

if not all_found:
    print("\n⚠ Some grid files are missing. You may need to download additional metallicities.")
else:
    print("\n✓ All essential grid files found!")

# Test 4: Try to load a grid
print("\nTest 4: Loading a sample grid...")
try:
    import h5py
    grid_file = POSYDON_DATA_PATH / "HMS-HMS_RLO/1e+00_Zsun.h5"
    with h5py.File(grid_file, 'r') as f:
        print(f"✓ Successfully opened {grid_file.name}")
        print(f"  Keys: {list(f.keys())[:5]}...")  # Show first 5 keys
except Exception as e:
    print(f"✗ Failed to load grid: {e}")
    all_found = False

# Test 5: Test basic POSYDON imports
print("\nTest 5: Testing POSYDON modules...")
try:
    from posydon.binary_evol.simulationproperties import SimulationProperties
    from posydon.binary_evol.binarystar import BinaryStar
    from posydon.binary_evol.flow_chart import flow_chart
    print("✓ Core POSYDON modules imported successfully")
except ImportError as e:
    print(f"✗ Failed to import POSYDON modules: {e}")
    all_found = False

# Test 6: Check auxiliary data
print("\nTest 6: Checking auxiliary data...")
aux_data = [
    "Couch+2020/Sukhbold_Mzams_He_c_core.csv",
    "Patton+Sukhbold20/Kepler_M4_table.dat",
]

for data_file in aux_data:
    data_path = POSYDON_DATA_PATH / data_file
    if data_path.exists():
        print(f"✓ Found {data_file}")
    else:
        print(f"⚠ Missing {data_file} (optional)")

# Summary
print("\n" + "="*60)
if all_found:
    print("✅ ALL TESTS PASSED!")
    print("\nPOSYDON is properly configured and ready to use.")
    print("\nNext steps:")
    print("1. Open CE_research_project.ipynb")
    print("2. Run the cells to start your research")
    print("3. Or run: python run_population.py --n_systems 1 --output test.h5")
else:
    print("⚠ SOME TESTS FAILED")
    print("\nPlease check the errors above and ensure:")
    print("1. POSYDON is installed: conda activate posydon")
    print("2. All grid files are extracted properly")
    print("3. The PATH_TO_POSYDON_DATA environment variable is set")

print("="*60)
