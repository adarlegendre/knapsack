"""
Benchmark all JSON files and regenerate graphs with complete data.
This script benchmarks all test cases and combines results, then generates graphs.
"""

import json
import csv
import os
import subprocess
import sys
from typing import Dict, List, Set

def get_existing_test_files(csv_file: str) -> Set[str]:
    """Get set of test files already in CSV."""
    existing = set()
    if os.path.exists(csv_file):
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                test_file = row.get('test_file', '')
                # Normalize path
                if test_file:
                    existing.add(os.path.basename(test_file))
    return existing

def get_all_json_files(results_dir: str) -> List[str]:
    """Get all JSON test files."""
    json_files = []
    if os.path.exists(results_dir):
        for filename in os.listdir(results_dir):
            if filename.startswith('test_') and filename.endswith('.json'):
                json_files.append(filename)
    # Sort by number
    json_files.sort(key=lambda x: int(x.split('_')[1].split('.')[0]) if x.split('_')[1].split('.')[0].isdigit() else 0)
    return json_files

def main():
    results_dir = 'results'
    csv_file = 'results/overnight_benchmark_results.csv'
    
    print("=" * 80)
    print("Benchmarking All Test Cases and Regenerating Graphs")
    print("=" * 80)
    
    # Get all JSON files
    all_json_files = get_all_json_files(results_dir)
    print(f"\nFound {len(all_json_files)} JSON test files")
    
    # Get existing test files from CSV
    existing_files = get_existing_test_files(csv_file)
    print(f"Found {len(existing_files)} test files already in CSV")
    
    # Find missing files
    missing_files = [f for f in all_json_files if f not in existing_files]
    if missing_files:
        print(f"\nFound {len(missing_files)} test files not yet benchmarked:")
        for f in missing_files[:10]:  # Show first 10
            print(f"  - {f}")
        if len(missing_files) > 10:
            print(f"  ... and {len(missing_files) - 10} more")
    else:
        print("\nAll test files are already benchmarked!")
    
    # Run benchmark.py on all files
    print("\n" + "=" * 80)
    print("Running benchmarks on all test files...")
    print("=" * 80)
    
    # Run benchmark.py which will process all JSON files
    result = subprocess.run([sys.executable, 'benchmark.py', results_dir, csv_file], 
                          capture_output=False)
    
    if result.returncode != 0:
        print(f"\nError: Benchmark script failed with return code {result.returncode}")
        return
    
    # Now regenerate graphs
    print("\n" + "=" * 80)
    print("Regenerating graphs...")
    print("=" * 80)
    
    result = subprocess.run([sys.executable, 'visualize_results.py', csv_file],
                          capture_output=False)
    
    if result.returncode != 0:
        print(f"\nError: Visualization script failed with return code {result.returncode}")
        return
    
    print("\n" + "=" * 80)
    print("Done! Graphs regenerated with all benchmark data.")
    print("=" * 80)

if __name__ == "__main__":
    main()

