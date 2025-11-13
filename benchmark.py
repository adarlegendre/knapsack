"""
Benchmark Script
Runs all knapsack solutions on test cases and collects performance metrics.

Measures execution time for each solution and exports results to CSV for analysis.
Handles timeouts and errors gracefully.
"""

import json
import csv
import time
import os
import signal
from typing import Dict, List, Optional, Tuple
from contextlib import contextmanager

# Import solution functions
from solution_dp_bottomup import knapsack_dp_bottomup
from solution_dp_topdown import knapsack_dp_topdown
from solution_graph_statespace import knapsack_graph_statespace
from solution_graph_dag import knapsack_graph_dag
from graph_counter import count_graph_nodes_edges

# Timeout in seconds (5 minutes default)
TIMEOUT_SECONDS = 300

class TimeoutError(Exception):
    """Custom timeout exception."""
    pass

@contextmanager
def timeout(seconds):
    """Context manager for function timeout (Unix only)."""
    def timeout_handler(signum, frame):
        raise TimeoutError(f"Function timed out after {seconds} seconds")
    
    # Set signal handler
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
    
    try:
        yield
    finally:
        signal.alarm(0)  # Cancel alarm

def run_with_timeout(func, *args, timeout_sec=TIMEOUT_SECONDS, **kwargs):
    """
    Run a function with timeout.
    
    Note: On Windows, we use simple timing checks since signal.SIGALRM is not available.
    The function will complete and then we check if it exceeded the timeout.
    For true timeout interruption on Windows, consider using multiprocessing.
    
    Args:
        func: Function to run
        *args: Positional arguments
        timeout_sec: Timeout in seconds
        **kwargs: Keyword arguments
        
    Returns:
        Tuple of (result, status, actual_time_seconds)
        - result: Function result or None if timeout/error
        - status: "SUCCESS", "TIMEOUT", or "ERROR: ..."
        - actual_time_seconds: Actual execution time (even if timeout)
    """
    start_time = time.perf_counter()
    
    try:
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start_time
        
        if elapsed > timeout_sec:
            return None, "TIMEOUT", elapsed
        
        return result, "SUCCESS", elapsed
    except Exception as e:
        elapsed = time.perf_counter() - start_time
        return None, f"ERROR: {str(e)}", elapsed

def benchmark_solution(solution_name: str, solution_func, items: List[Dict], 
                       capacity: int) -> Tuple[Optional[float], str, Optional[float]]:
    """
    Benchmark a single solution.
    
    Args:
        solution_name: Name of the solution
        solution_func: Solution function
        items: List of items
        capacity: Capacity
        
    Returns:
        Tuple of (execution_time_ms, status, actual_time_ms)
        - execution_time_ms: Time if successful, None if timeout/error
        - status: "SUCCESS", "TIMEOUT", or "ERROR: ..."
        - actual_time_ms: Actual execution time (even if timeout occurred)
    """
    try:
        result, status, actual_time_sec = run_with_timeout(solution_func, items, capacity, 
                                                           timeout_sec=TIMEOUT_SECONDS)
        
        actual_time_ms = actual_time_sec * 1000  # Convert to milliseconds
        
        if status == "SUCCESS" and result is not None:
            return actual_time_ms, "SUCCESS", actual_time_ms
        else:
            # Return None for recorded time, but include actual time for reference
            return None, status, actual_time_ms
    except Exception as e:
        return None, f"ERROR: {str(e)}", None

def benchmark_test_case(test_file: str) -> Dict:
    """
    Benchmark all solutions on a single test case.
    
    Args:
        test_file: Path to test case JSON file
        
    Returns:
        Dictionary with benchmark results
    """
    # Load test case
    with open(test_file, 'r') as f:
        data = json.load(f)
    
    items = data['items']
    capacity = data['capacity']
    metadata = data.get('metadata', {})
    
    # Count actual graph size
    try:
        actual_nodes, actual_edges = count_graph_nodes_edges(items, capacity)
    except Exception as e:
        actual_nodes, actual_edges = None, None
    
    results = {
        'test_file': test_file,
        'target_nodes': metadata.get('target_nodes', 'N/A'),
        'actual_nodes': actual_nodes,
        'actual_edges': actual_edges,
        'num_items': len(items),
        'capacity': capacity
    }
    
    # Benchmark each solution
    solutions = [
        ('dp_bottomup', knapsack_dp_bottomup),
        ('dp_topdown', knapsack_dp_topdown),
        ('graph_statespace', knapsack_graph_statespace),
        ('graph_dag', knapsack_graph_dag)
    ]
    
    for sol_name, sol_func in solutions:
        print(f"  Running {sol_name}...", end=' ', flush=True)
        time_ms, status, actual_time_ms = benchmark_solution(sol_name, sol_func, items, capacity)
        
        results[f'{sol_name}_time'] = time_ms if time_ms else None
        results[f'{sol_name}_status'] = status
        results[f'{sol_name}_actual_time'] = actual_time_ms if actual_time_ms else None
        
        if time_ms:
            print(f"[OK] {time_ms:.2f} ms")
        elif actual_time_ms:
            # Show actual time even if timeout
            print(f"[TIMEOUT] {actual_time_ms:.2f} ms (exceeded {TIMEOUT_SECONDS}s limit)")
        else:
            print(f"[FAIL] {status}")
    
    return results

def benchmark_all(test_dir: str = 'results', output_file: str = 'results/benchmark_results.csv'):
    """
    Benchmark all test cases in a directory.
    
    Args:
        test_dir: Directory containing test case files
        output_file: Output CSV file path
    """
    # Find all test case files
    test_files = []
    if os.path.exists(test_dir):
        for filename in os.listdir(test_dir):
            if filename.startswith('test_') and filename.endswith('.json'):
                test_files.append(os.path.join(test_dir, filename))
    
    # Sort by target size (extract from filename)
    test_files.sort(key=lambda x: int(x.split('_')[1].split('.')[0]) if x.split('_')[1].split('.')[0].isdigit() else 0)
    
    if not test_files:
        print(f"No test files found in {test_dir}")
        print("Run test_generator.py first to generate test cases.")
        return
    
    print("=" * 80)
    print("Benchmarking Knapsack Solutions")
    print("=" * 80)
    print(f"Found {len(test_files)} test cases")
    print(f"Timeout: {TIMEOUT_SECONDS} seconds per solution")
    print()
    
    all_results = []
    
    for i, test_file in enumerate(test_files, 1):
        print(f"[{i}/{len(test_files)}] {os.path.basename(test_file)}")
        
        try:
            result = benchmark_test_case(test_file)
            all_results.append(result)
        except Exception as e:
            print(f"  [FAILED] Failed to benchmark: {e}")
            continue
        
        print()
    
    # Write results to CSV
    if all_results:
        os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
        
        fieldnames = [
            'test_file', 'target_nodes', 'actual_nodes', 'actual_edges',
            'num_items', 'capacity',
            'dp_bottomup_time', 'dp_bottomup_status', 'dp_bottomup_actual_time',
            'dp_topdown_time', 'dp_topdown_status', 'dp_topdown_actual_time',
            'graph_statespace_time', 'graph_statespace_status', 'graph_statespace_actual_time',
            'graph_dag_time', 'graph_dag_status', 'graph_dag_actual_time'
        ]
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_results)
        
        print("=" * 80)
        print(f"Results saved to: {output_file}")
        print("=" * 80)
        
        # Print summary
        print("\nSummary:")
        print(f"{'Nodes':>10} {'DP-BU (ms)':>12} {'DP-TD (ms)':>12} {'Graph-SS (ms)':>15} {'Graph-DAG (ms)':>15}")
        print("-" * 80)
        
        for result in all_results:
            nodes = result.get('actual_nodes', 'N/A')
            
            # Show actual time if available (even on timeout), otherwise show status
            dp_bu = _format_result(result, 'dp_bottomup')
            dp_td = _format_result(result, 'dp_topdown')
            g_ss = _format_result(result, 'graph_statespace')
            g_dag = _format_result(result, 'graph_dag')
            
            print(f"{nodes:>10} {dp_bu:>12} {dp_td:>12} {g_ss:>15} {g_dag:>15}")

def _format_result(result: Dict, solution_name: str) -> str:
    """Format result for display, showing actual time if available."""
    time_ms = result.get(f'{solution_name}_time')
    actual_time_ms = result.get(f'{solution_name}_actual_time')
    status = result.get(f'{solution_name}_status', 'N/A')
    
    if time_ms:
        return f"{time_ms:.2f}"
    elif actual_time_ms:
        # Show actual time with timeout indicator
        return f"{actual_time_ms:.2f}*"
    else:
        return status[:12]  # Truncate long error messages

def main():
    """CLI interface for benchmark."""
    import sys
    
    test_dir = sys.argv[1] if len(sys.argv) > 1 else 'results'
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'results/benchmark_results.csv'
    
    benchmark_all(test_dir, output_file)

if __name__ == "__main__":
    # Note: Timeout functionality using signal.SIGALRM only works on Unix systems
    # On Windows, we use simple timing checks instead
    if os.name == 'nt':
        print("Note: Running on Windows - timeout uses simple timing (not signal-based)")
        print()
    
    main()

