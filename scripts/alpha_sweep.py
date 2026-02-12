#!/usr/bin/env python3
"""
Unified Alpha Sweep Script with Error Handling and Checkpointing

This script replaces run_alpha_sweep.sh with a robust Python implementation
that includes:
- Checkpointing (skip completed simulations)
- Error recovery (continue on failure)
- Progress tracking
- File validation
- Automatic analysis integration

Usage:
    python alpha_sweep.py                    # Run all simulations
    python alpha_sweep.py --resume           # Resume from checkpoint
    python alpha_sweep.py --analyze-only     # Skip sims, just analyze
    python alpha_sweep.py --dry-run          # See what would run
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np

# ============================================================================
# Configuration
# ============================================================================

SIMULATIONS = [
    {
        'name': 'Low Z, α=1.0',
        'metallicity': 0.001,
        'alpha_CE': 1.0,
        'output': 'data/low_Z_alpha1p0.h5',
        'n_systems': 200,
        'params': {
            'M1_min': 10, 'M1_max': 20, 'M1_samples': 10,
            'M2_min': 8, 'M2_max': 15, 'M2_samples': 10,
            'P_min': 50, 'P_max': 500, 'P_samples': 20
        }
    },
    {
        'name': 'Low Z, α=2.0',
        'metallicity': 0.001,
        'alpha_CE': 2.0,
        'output': 'data/low_Z_alpha2p0.h5',
        'n_systems': 200,
        'params': {
            'M1_min': 10, 'M1_max': 20, 'M1_samples': 10,
            'M2_min': 8, 'M2_max': 15, 'M2_samples': 10,
            'P_min': 50, 'P_max': 500, 'P_samples': 20
        }
    },
    {
        'name': 'Mid Z, α=1.0',
        'metallicity': 0.006,
        'alpha_CE': 1.0,
        'output': 'data/mid_Z_alpha1p0.h5',
        'n_systems': 200,
        'params': {
            'M1_min': 10, 'M1_max': 20, 'M1_samples': 10,
            'M2_min': 8, 'M2_max': 15, 'M2_samples': 10,
            'P_min': 50, 'P_max': 500, 'P_samples': 20
        }
    },
    {
        'name': 'Mid Z, α=2.0',
        'metallicity': 0.006,
        'alpha_CE': 2.0,
        'output': 'data/mid_Z_alpha2p0.h5',
        'n_systems': 200,
        'params': {
            'M1_min': 10, 'M1_max': 20, 'M1_samples': 10,
            'M2_min': 8, 'M2_max': 15, 'M2_samples': 10,
            'P_min': 50, 'P_max': 500, 'P_samples': 20
        }
    }
]

CHECKPOINT_FILE = 'alpha_sweep_progress.json'
LOG_FILE = 'alpha_sweep.log'

# ============================================================================
# Utility Functions
# ============================================================================

def log(message, level='INFO'):
    """Write timestamped message to console and log file."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f"[{timestamp}] {level}: {message}"
    print(log_message)
    
    with open(LOG_FILE, 'a') as f:
        f.write(log_message + '\n')

def load_checkpoint():
    """Load progress from checkpoint file."""
    if Path(CHECKPOINT_FILE).exists():
        try:
            with open(CHECKPOINT_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            log(f"Error loading checkpoint: {e}", 'WARNING')
            return {}
    return {}

def save_checkpoint(checkpoint):
    """Save progress to checkpoint file."""
    try:
        with open(CHECKPOINT_FILE, 'w') as f:
            json.dump(checkpoint, indent=2, fp=f)
        log(f"Checkpoint saved to {CHECKPOINT_FILE}")
    except Exception as e:
        log(f"Error saving checkpoint: {e}", 'ERROR')

def validate_hdf5(filepath):
    """Check if HDF5 file is valid and contains data."""
    try:
        df = pd.read_hdf(filepath, 'results')
        
        # Check if file has data
        if len(df) == 0:
            log(f"File {filepath} is empty", 'WARNING')
            return False
        
        # Check for required columns
        required_cols = ['M1_initial', 'M2_initial', 'P_initial', 'Z']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            log(f"File {filepath} missing columns: {missing_cols}", 'WARNING')
            return False
        
        log(f"File {filepath} validated: {len(df)} systems")
        return True
        
    except Exception as e:
        log(f"Error validating {filepath}: {e}", 'ERROR')
        return False

def check_prerequisites():
    """Check if baseline simulations exist."""
    required_files = [
        'data/ce_fixed_lambda.h5',
        'data/mid_Z_lambda.h5',
        'data/low_Z_lambda.h5'
    ]
    
    missing = []
    for file in required_files:
        if not Path(file).exists():
            missing.append(file)
    
    if missing:
        log("WARNING: Some baseline files not found:", 'WARNING')
        for file in missing:
            log(f"  - {file}", 'WARNING')
        log("These are optional but recommended for comparison", 'INFO')
    
    return True

# ============================================================================
# Simulation Runner
# ============================================================================

def build_command(sim_config):
    """Build the command to run a simulation."""
    cmd = [
        'python', 'run_population.py',
        '--metallicity', str(sim_config['metallicity']),
        '--alpha_CE', str(sim_config['alpha_CE']),
        '--n_systems', str(sim_config['n_systems']),
        '--output', sim_config['output']
    ]
    
    # Add parameter ranges
    for key, value in sim_config['params'].items():
        cmd.extend([f'--{key}', str(value)])
    
    return cmd

def run_simulation(sim_config, dry_run=False):
    """Run a single simulation with error handling."""
    log(f"Starting: {sim_config['name']}")
    log(f"  Metallicity: {sim_config['metallicity']}")
    log(f"  Alpha CE: {sim_config['alpha_CE']}")
    log(f"  Output: {sim_config['output']}")
    log(f"  Systems: {sim_config['n_systems']}")
    
    cmd = build_command(sim_config)
    
    if dry_run:
        log(f"DRY RUN - Would execute: {' '.join(cmd)}")
        return True, "Dry run - not executed"
    
    try:
        start_time = datetime.now()
        log(f"Command: {' '.join(cmd)}")
        
        # Run simulation
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=7200  # 2 hour timeout per simulation
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds() / 60
        
        if result.returncode == 0:
            log(f"✓ Simulation completed successfully in {duration:.1f} minutes")
            
            # Validate output
            if validate_hdf5(sim_config['output']):
                return True, f"Success ({duration:.1f} min)"
            else:
                return False, "Output validation failed"
        else:
            log(f"✗ Simulation failed with return code {result.returncode}", 'ERROR')
            log(f"stderr: {result.stderr}", 'ERROR')
            return False, f"Exit code {result.returncode}"
            
    except subprocess.TimeoutExpired:
        log(f"✗ Simulation timed out after 2 hours", 'ERROR')
        return False, "Timeout"
    except Exception as e:
        log(f"✗ Unexpected error: {e}", 'ERROR')
        return False, str(e)

# ============================================================================
# Main Orchestrator
# ============================================================================

def run_sweep(args):
    """Run the complete alpha sweep."""
    
    log("="*70)
    log("ALPHA SWEEP - UNIFIED RUNNER")
    log("="*70)
    
    # Check prerequisites
    if not args.skip_checks:
        log("\nChecking prerequisites...")
        check_prerequisites()
    
    # Load checkpoint
    checkpoint = load_checkpoint() if args.resume else {}
    
    if args.resume and checkpoint:
        log(f"\nResuming from checkpoint: {len(checkpoint)} simulations tracked")
    
    # Check what needs to be run
    log("\nScanning simulation status...")
    to_run = []
    skipped = []
    
    for sim in SIMULATIONS:
        output_file = Path(sim['output'])
        
        # Check if already completed
        if output_file.exists():
            if validate_hdf5(output_file):
                log(f"✓ {sim['name']}: Already complete ({sim['output']})")
                skipped.append(sim)
                continue
            else:
                log(f"⚠ {sim['name']}: File exists but invalid, will re-run")
        
        # Check checkpoint
        if sim['name'] in checkpoint:
            status = checkpoint[sim['name']].get('status')
            if status == 'complete':
                log(f"✓ {sim['name']}: Marked complete in checkpoint")
                skipped.append(sim)
                continue
        
        to_run.append(sim)
    
    # Summary
    log(f"\nSimulation plan:")
    log(f"  To run: {len(to_run)}")
    log(f"  Skipped (complete): {len(skipped)}")
    
    if len(to_run) == 0:
        log("\n✓ All simulations complete!")
        return True
    
    if args.dry_run:
        log("\nDRY RUN - Simulations to execute:")
        for sim in to_run:
            log(f"  • {sim['name']}")
        return True
    
    # Confirmation
    if not args.yes:
        log(f"\nThis will run {len(to_run)} simulations (~90 min each)")
        log(f"Estimated runtime: {len(to_run) * 90 / 60:.1f} hours")
        response = input("\nContinue? [y/N]: ")
        if response.lower() != 'y':
            log("Aborted by user")
            return False
    
    # Run simulations
    log("\n" + "="*70)
    log("STARTING SIMULATIONS")
    log("="*70)
    
    total_start = datetime.now()
    successes = 0
    failures = 0
    
    for i, sim in enumerate(to_run, 1):
        log(f"\n[{i}/{len(to_run)}] {sim['name']}")
        log("-"*70)
        
        success, message = run_simulation(sim, dry_run=args.dry_run)
        
        # Update checkpoint
        checkpoint[sim['name']] = {
            'status': 'complete' if success else 'failed',
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        save_checkpoint(checkpoint)
        
        if success:
            successes += 1
        else:
            failures += 1
            if args.stop_on_error:
                log("\nStopping due to error (--stop-on-error)", 'ERROR')
                break
    
    # Final summary
    total_time = (datetime.now() - total_start).total_seconds() / 60
    
    log("\n" + "="*70)
    log("SIMULATION SWEEP COMPLETE")
    log("="*70)
    log(f"\nTotal runtime: {total_time:.1f} minutes")
    log(f"Successes: {successes}")
    log(f"Failures: {failures}")
    log(f"Skipped: {len(skipped)}")
    
    if failures > 0:
        log("\n⚠ Some simulations failed. Check log for details.", 'WARNING')
        return False
    
    return True

def run_analysis():
    """Run the alpha sweep analysis script."""
    log("\n" + "="*70)
    log("RUNNING ANALYSIS")
    log("="*70)
    
    try:
        result = subprocess.run(
            ['python', 'analyze_alpha_sweep.py'],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            log("✓ Analysis completed successfully")
            print(result.stdout)
            return True
        else:
            log("✗ Analysis failed", 'ERROR')
            log(result.stderr, 'ERROR')
            return False
    except Exception as e:
        log(f"✗ Error running analysis: {e}", 'ERROR')
        return False

# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Alpha CE sweep with checkpointing and error recovery',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python alpha_sweep.py                 # Run all simulations
  python alpha_sweep.py --resume        # Resume from checkpoint
  python alpha_sweep.py --dry-run       # See what would run
  python alpha_sweep.py --analyze-only  # Skip sims, just analyze
  python alpha_sweep.py --yes           # Skip confirmation prompt
        """
    )
    
    parser.add_argument('--resume', action='store_true',
                       help='Resume from checkpoint (skip completed sims)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would run without executing')
    parser.add_argument('--analyze-only', action='store_true',
                       help='Skip simulations, only run analysis')
    parser.add_argument('--stop-on-error', action='store_true',
                       help='Stop if any simulation fails')
    parser.add_argument('--skip-checks', action='store_true',
                       help='Skip prerequisite file checks')
    parser.add_argument('--yes', '-y', action='store_true',
                       help='Skip confirmation prompt')
    parser.add_argument('--analyze', action='store_true',
                       help='Run analysis after simulations complete')
    
    args = parser.parse_args()
    
    # Clear log at start (unless resuming)
    if not args.resume:
        with open(LOG_FILE, 'w') as f:
            f.write(f"Alpha sweep started: {datetime.now()}\n")
    
    # Run simulations (unless analyze-only)
    if not args.analyze_only:
        success = run_sweep(args)
        
        if not success and not args.dry_run:
            log("\n✗ Simulation sweep incomplete", 'ERROR')
            sys.exit(1)
    
    # Run analysis if requested
    if args.analyze or args.analyze_only:
        analysis_success = run_analysis()
        if not analysis_success:
            sys.exit(1)
    
    log("\n✓ All tasks complete!")
    log(f"Log saved to: {LOG_FILE}")
    log(f"Checkpoint: {CHECKPOINT_FILE}")

if __name__ == '__main__':
    main()
