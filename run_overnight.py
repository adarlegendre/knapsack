"""
Overnight Benchmarking Script
Runs test generation and benchmarking without timeout restrictions.
Designed to run unattended overnight.

Usage:
    python run_overnight.py [target_sizes]
    
Example:
    python run_overnight.py 500 1000 5000 10000 50000 100000
"""

import sys
import os
import json
import time
import csv
import gc
from datetime import datetime
from typing import List, Dict, Optional

# Import modules
from test_generator import generate_test_cases, find_closest_test_case
from graph_counter import count_graph_nodes_edges
from solution_dp_bottomup import knapsack_dp_bottomup
from solution_dp_topdown import knapsack_dp_topdown
from solution_graph_statespace import knapsack_graph_statespace
from solution_graph_dag import knapsack_graph_dag
from visualize_results import generate_all_graphs

# NO TIMEOUT - Let solutions run as long as needed
NO_TIMEOUT = float('inf')

def log_message(message: str, log_file: str = 'overnight_log.txt'):
    """Log message with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(log_entry + '\n')

def benchmark_solution_no_timeout(solution_name: str, solution_func, items: List[Dict], 
                                   capacity: int) -> tuple:
    """
    Benchmark a solution without timeout restrictions.
    
    Returns:
        Tuple of (execution_time_ms, status, actual_time_ms)
    """
    start_time = time.perf_counter()
    
    try:
        result = solution_func(items, capacity)
        elapsed = time.perf_counter() - start_time
        elapsed_ms = elapsed * 1000
        
        if result:
            return elapsed_ms, "SUCCESS", elapsed_ms
        else:
            return None, "ERROR: No result", elapsed_ms
    except Exception as e:
        elapsed = time.perf_counter() - start_time
        elapsed_ms = elapsed * 1000
        return None, f"ERROR: {str(e)}", elapsed_ms

def benchmark_test_case_no_timeout(test_file: str, skip_graph_solutions: bool = False) -> Dict:
    """
    Benchmark all solutions on a test case without timeout.
    """
    # Load test case
    with open(test_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    items = data['items']
    capacity = data['capacity']
    metadata = data.get('metadata', {})
    
    # Use metadata if available (much faster than recounting)
    # Only count if metadata is missing (for backward compatibility)
    if 'actual_nodes' in metadata and 'actual_edges' in metadata:
        actual_nodes = metadata['actual_nodes']
        actual_edges = metadata['actual_edges']
    else:
        # Count actual graph size (only if metadata missing)
        try:
            actual_nodes, actual_edges = count_graph_nodes_edges(items, capacity)
        except Exception as e:
            log_message(f"Warning: Could not count graph size: {e}")
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
    ]
    
    # Only add graph solutions if not skipping
    if not skip_graph_solutions:
        solutions.extend([
            ('graph_statespace', knapsack_graph_statespace),
            ('graph_dag', knapsack_graph_dag)
        ])
    else:
        # Set graph solutions to skipped status
        results['graph_statespace_time'] = None
        results['graph_statespace_status'] = 'SKIPPED (large size)'
        results['graph_statespace_actual_time'] = None
        results['graph_dag_time'] = None
        results['graph_dag_status'] = 'SKIPPED (large size)'
        results['graph_dag_actual_time'] = None
    
    test_case_start = time.perf_counter()
    num_solutions = len(solutions)
    
    for sol_idx, (sol_name, sol_func) in enumerate(solutions, 1):
        sol_start = time.perf_counter()
        print(f"  [{sol_idx}/{num_solutions}] Running {sol_name}...", end=' ', flush=True)
        log_message(f"  [{sol_idx}/{num_solutions}] Running {sol_name}...")
        
        time_ms, status, actual_time_ms = benchmark_solution_no_timeout(
            sol_name, sol_func, items, capacity
        )
        
        sol_elapsed = time.perf_counter() - sol_start
        sol_elapsed_sec = sol_elapsed
        sol_elapsed_str = f"{int(sol_elapsed_sec//60)}m {int(sol_elapsed_sec%60)}s" if sol_elapsed_sec >= 60 else f"{sol_elapsed_sec:.1f}s"
        
        results[f'{sol_name}_time'] = time_ms if time_ms else None
        results[f'{sol_name}_status'] = status
        results[f'{sol_name}_actual_time'] = actual_time_ms if actual_time_ms else None
        
        # Show progress within test case
        test_case_elapsed = time.perf_counter() - test_case_start
        remaining_sols = num_solutions - sol_idx
        if remaining_sols > 0 and sol_idx > 0:
            avg_time_per_sol = test_case_elapsed / sol_idx
            est_remaining = avg_time_per_sol * remaining_sols
            est_remaining_str = f"{int(est_remaining//60)}m {int(est_remaining%60)}s" if est_remaining >= 60 else f"{est_remaining:.1f}s"
            progress_pct = int((sol_idx / num_solutions) * 100)
            print(f"[OK] {time_ms:.2f} ms ({sol_elapsed_str}) | Test progress: {progress_pct}% | Est. remaining: {est_remaining_str}")
        else:
            if time_ms:
                print(f"[OK] {time_ms:.2f} ms ({sol_elapsed_str})")
            elif actual_time_ms:
                print(f"[TIMEOUT] {actual_time_ms:.2f} ms ({sol_elapsed_str})")
            else:
                print(f"[FAIL] {status} ({sol_elapsed_str})")
        
        if time_ms:
            log_message(f"    [OK] {time_ms:.2f} ms ({sol_elapsed_str})")
        elif actual_time_ms:
            log_message(f"    [TIMEOUT] {actual_time_ms:.2f} ms ({sol_elapsed_str})")
        else:
            log_message(f"    [FAIL] {status} ({sol_elapsed_str})")
    
    return results

def run_overnight_benchmark(target_sizes: List[int], 
                           test_dir: str = 'results',
                           output_file: str = 'results/overnight_benchmark_results.csv',
                           log_file: str = 'overnight_log.txt',
                           skip_graph_solutions_for_large: Optional[int] = 5000):
    """
    Run complete overnight benchmarking pipeline.
    
    Steps:
    1. Generate test cases (if they don't exist)
    2. Benchmark all test cases without timeout
    3. Save results to CSV
    """
    overall_start_time = time.perf_counter()
    
    # Clear/create log file
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"Overnight Benchmarking Session Started: {datetime.now()}\n")
        f.write("=" * 80 + "\n\n")
    
    log_message("=" * 80)
    log_message("Overnight Benchmarking - NO TIMEOUT RESTRICTIONS")
    log_message("=" * 80)
    log_message(f"Target sizes: {target_sizes}")
    log_message(f"Output: {output_file}")
    log_message("")
    
    # Step 1: Generate test cases (if needed)
    print("STEP 1: Generating test cases...")
    print("-" * 80)
    log_message("STEP 1: Generating test cases...")
    log_message("-" * 80)
    
    test_files = []
    gen_start_time = time.perf_counter()
    
    for idx, target_size in enumerate(target_sizes, 1):
        test_file = f"{test_dir}/test_{target_size}.json"
        
        if os.path.exists(test_file):
            print(f"  [{idx}/{len(target_sizes)}] Test case {target_size} already exists: {os.path.basename(test_file)}")
            log_message(f"  Test case {target_size} already exists: {test_file}")
            test_files.append(test_file)
        else:
            elapsed = time.perf_counter() - gen_start_time
            elapsed_str = f"{int(elapsed//3600):02d}:{int((elapsed%3600)//60):02d}:{int(elapsed%60):02d}"
            print(f"  [{idx}/{len(target_sizes)}] Generating test case for {target_size} nodes... (Elapsed: {elapsed_str})")
            log_message(f"  Generating test case for {target_size} nodes...")
            try:
                # Increase attempts for very large sizes (need more exploration)
                if target_size >= 50000:
                    max_attempts = 150  # More attempts for 50K+
                elif target_size >= 30000:
                    max_attempts = 125  # More attempts for 30K+
                elif target_size >= 20000:
                    max_attempts = 100
                elif target_size >= 5000:
                    max_attempts = 75
                else:
                    max_attempts = 50
                    
                test_case = find_closest_test_case(target_size, max_attempts=max_attempts)
                
                # Save test case
                output_data = {
                    'capacity': test_case['capacity'],
                    'items': test_case['items'],
                    'metadata': {
                        'target_nodes': target_size,
                        'actual_nodes': test_case['actual_nodes'],
                        'actual_edges': test_case['actual_edges'],
                        'num_items': test_case['num_items'],
                        'error': test_case['error']
                    }
                }
                
                os.makedirs(test_dir, exist_ok=True)
                with open(test_file, 'w', encoding='utf-8') as f:
                    json.dump(output_data, f, indent=2)
                
                elapsed = time.perf_counter() - gen_start_time
                elapsed_str = f"{int(elapsed//3600):02d}:{int((elapsed%3600)//60):02d}:{int(elapsed%60):02d}"
                print(f"    [OK] Generated: {os.path.basename(test_file)}")
                print(f"    Actual: {test_case['actual_nodes']} nodes, {test_case['actual_edges']} edges (Elapsed: {elapsed_str})")
                log_message(f"    [OK] Generated: {test_file}")
                log_message(f"    Actual: {test_case['actual_nodes']} nodes, "
                          f"{test_case['actual_edges']} edges")
                test_files.append(test_file)
            except Exception as e:
                print(f"    [FAILED] Could not generate {target_size}: {e}")
                log_message(f"    [FAILED] Could not generate {target_size}: {e}")
                continue
    
    gen_total = time.perf_counter() - gen_start_time
    gen_total_str = f"{int(gen_total//3600):02d}:{int((gen_total%3600)//60):02d}:{int(gen_total%60):02d}"
    print(f"\nTest case generation complete. Total time: {gen_total_str}")
    print(f"Generated {len(test_files)} test cases ready for benchmarking.\n")
    log_message("")
    
    # Step 2: Benchmark all test cases (with resume support)
    print("STEP 2: Benchmarking all test cases (NO TIMEOUT)...")
    print("-" * 80)
    log_message("STEP 2: Benchmarking all test cases (NO TIMEOUT)...")
    log_message("-" * 80)
    
    # Load existing results if CSV exists (for resume)
    existing_results = {}
    if os.path.exists(output_file):
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    test_file_path = row.get('test_file', '')
                    # Check if this test case has complete results
                    # For large sizes (>= 5000), graph solutions may be skipped
                    dp_complete = (row.get('dp_bottomup_status') == 'SUCCESS' and 
                                  row.get('dp_topdown_status') == 'SUCCESS')
                    graph_status = row.get('graph_statespace_status', '')
                    # Accept SUCCESS, TIMEOUT, ERROR, or SKIPPED (for large sizes)
                    graph_complete = graph_status in ['SUCCESS', 'TIMEOUT', 'ERROR', 'SKIPPED (large size)']
                    
                    if dp_complete and graph_complete:
                        existing_results[test_file_path] = row
                        log_message(f"  Found existing results for: {os.path.basename(test_file_path)}")
                    # Clear row from memory after processing
                    del row
        except Exception as e:
            log_message(f"  Warning: Could not load existing results: {e}")
        finally:
            gc.collect()  # Free memory after loading existing results
    
    if existing_results:
        print(f"  Resuming: {len(existing_results)} test cases already completed")
        log_message(f"  Resuming: {len(existing_results)} test cases already completed")
        log_message("")
    
    # Prepare CSV file for incremental writing
    fieldnames = [
        'test_file', 'target_nodes', 'actual_nodes', 'actual_edges',
        'num_items', 'capacity',
        'dp_bottomup_time', 'dp_bottomup_status', 'dp_bottomup_actual_time',
        'dp_topdown_time', 'dp_topdown_status', 'dp_topdown_actual_time',
        'graph_statespace_time', 'graph_statespace_status', 'graph_statespace_actual_time',
        'graph_dag_time', 'graph_dag_status', 'graph_dag_actual_time'
    ]
    
    # Open CSV file for incremental writing
    csv_file_exists = os.path.exists(output_file)
    csv_file = open(output_file, 'a' if csv_file_exists else 'w', newline='', encoding='utf-8')
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    
    # Write header if new file
    if not csv_file_exists:
        writer.writeheader()
        csv_file.flush()
    
    all_results = []  # Keep for summary at end
    completed_count = 0
    total_tests = len(test_files)
    start_time = time.perf_counter()
    test_times = []  # Track time per test case for ETA calculation
    
    for i, test_file in enumerate(test_files, 1):
        test_case_start_time = time.perf_counter()
        
        # Check if already completed
        if test_file in existing_results:
            print(f"[{i}/{len(test_files)}] {os.path.basename(test_file)} [SKIP - Already completed]")
            log_message(f"[{i}/{len(test_files)}] {os.path.basename(test_file)} [SKIP - Already completed]")
            result = existing_results[test_file]
            all_results.append(result)
            completed_count += 1
            continue
        
        # Calculate progress and ETA
        elapsed = time.perf_counter() - start_time
        elapsed_str = f"{int(elapsed//3600):02d}:{int((elapsed%3600)//60):02d}:{int(elapsed%60):02d}"
        remaining_tests = len(test_files) - i
        progress_pct = int((i / total_tests) * 100)
        
        # Calculate estimated time remaining based on average time per test
        if test_times:
            avg_time_per_test = sum(test_times) / len(test_times)
            est_remaining_sec = avg_time_per_test * remaining_tests
            est_remaining_str = f"{int(est_remaining_sec//3600):02d}:{int((est_remaining_sec%3600)//60):02d}:{int(est_remaining_sec%60):02d}"
            est_completion = time.perf_counter() + est_remaining_sec
            est_completion_time = datetime.fromtimestamp(est_completion).strftime("%H:%M:%S")
            print(f"\n[{i}/{len(test_files)}] {os.path.basename(test_file)}")
            print(f"  Progress: {progress_pct}% | Elapsed: {elapsed_str} | Remaining tests: {remaining_tests}")
            print(f"  Est. time remaining: {est_remaining_str} | Est. completion: {est_completion_time}")
        else:
            print(f"\n[{i}/{len(test_files)}] {os.path.basename(test_file)}")
            print(f"  Progress: {progress_pct}% | Elapsed: {elapsed_str} | Remaining tests: {remaining_tests}")
            print(f"  Est. time remaining: Calculating... (after first test)")
        
        log_message(f"[{i}/{len(test_files)}] {os.path.basename(test_file)}")
        log_message(f"  Progress: {progress_pct}% | Elapsed: {elapsed_str} | Remaining: {remaining_tests}")
        
        try:
            # Check if we should skip graph solutions for large sizes (>= 5000 nodes)
            skip_graph = False
            if skip_graph_solutions_for_large is not None:
                with open(test_file, 'r', encoding='utf-8') as f:
                    test_data = json.load(f)
                actual_nodes = test_data.get('metadata', {}).get('actual_nodes', 0)
                skip_graph = actual_nodes >= skip_graph_solutions_for_large if actual_nodes else False
                del test_data  # Free memory
                
                if skip_graph:
                    print(f"  Note: Skipping graph solutions for large size ({actual_nodes} nodes)")
                    log_message(f"  Note: Skipping graph solutions for large size ({actual_nodes} nodes)")
            
            result = benchmark_test_case_no_timeout(test_file, skip_graph_solutions=skip_graph)
            
            # Write result immediately to CSV (incremental save)
            writer.writerow(result)
            csv_file.flush()  # Ensure data is written to disk
            
            all_results.append(result)
            
            # Track time for this test case
            test_case_elapsed = time.perf_counter() - test_case_start_time
            test_times.append(test_case_elapsed)
            
            # Show completion status with statistics
            elapsed = time.perf_counter() - start_time
            elapsed_str = f"{int(elapsed//3600):02d}:{int((elapsed%3600)//60):02d}:{int(elapsed%60):02d}"
            test_case_time_str = f"{int(test_case_elapsed//60)}m {int(test_case_elapsed%60)}s" if test_case_elapsed >= 60 else f"{test_case_elapsed:.1f}s"
            
            # Calculate running statistics
            if len(test_times) > 0:
                avg_time = sum(test_times) / len(test_times)
                avg_time_str = f"{int(avg_time//60)}m {int(avg_time%60)}s" if avg_time >= 60 else f"{avg_time:.1f}s"
                remaining_tests = total_tests - i
                if remaining_tests > 0:
                    est_remaining_sec = avg_time * remaining_tests
                    est_remaining_str = f"{int(est_remaining_sec//3600):02d}:{int((est_remaining_sec%3600)//60):02d}:{int(est_remaining_sec%60):02d}"
                    print(f"  [COMPLETE] Test case finished in {test_case_time_str}")
                    print(f"  Average time per test: {avg_time_str} | Est. remaining: {est_remaining_str}")
                else:
                    print(f"  [COMPLETE] Test case finished in {test_case_time_str}")
                    print(f"  Average time per test: {avg_time_str} | All tests complete!")
            else:
                print(f"  [COMPLETE] Test case finished in {test_case_time_str}")
            
            print()  # Blank line for readability
            log_message(f"  [COMPLETE] Test case finished in {test_case_time_str}")
            log_message("")
            
            # Force garbage collection after each test case to free memory
            del result
            gc.collect()
            
        except MemoryError as e:
            log_message(f"  [MEMORY ERROR] Out of memory: {e}")
            log_message("  Consider skipping graph solutions for this size")
            log_message("")
            gc.collect()  # Try to free memory
            continue
        except Exception as e:
            log_message(f"  [FAILED] Error: {e}")
            log_message("")
            gc.collect()
            continue
        
        # Progress update (already shown above, but log for completeness)
        elapsed = time.perf_counter() - start_time
        elapsed_str = time.strftime("%H:%M:%S", time.gmtime(elapsed))
        remaining_tests = total_tests - i
        progress_pct = int((i / total_tests) * 100)
        if test_times:
            avg_time = sum(test_times) / len(test_times)
            est_remaining_sec = avg_time * remaining_tests if remaining_tests > 0 else 0
            est_remaining_str = time.strftime("%H:%M:%S", time.gmtime(est_remaining_sec))
            log_message(f"  Progress: {i}/{total_tests} ({progress_pct}%) | Elapsed: {elapsed_str} | Est. remaining: {est_remaining_str}")
        else:
            log_message(f"  Progress: {i}/{total_tests} ({progress_pct}%) | Elapsed: {elapsed_str} | Remaining: {remaining_tests}")
    
    csv_file.close()  # Close CSV file
    
    # Final benchmarking statistics
    benchmark_total_time = time.perf_counter() - start_time
    benchmark_total_str = f"{int(benchmark_total_time//3600):02d}:{int((benchmark_total_time%3600)//60):02d}:{int(benchmark_total_time%60):02d}"
    
    if test_times:
        avg_test_time = sum(test_times) / len(test_times)
        min_test_time = min(test_times)
        max_test_time = max(test_times)
        avg_str = f"{int(avg_test_time//60)}m {int(avg_test_time%60)}s" if avg_test_time >= 60 else f"{avg_test_time:.1f}s"
        min_str = f"{int(min_test_time//60)}m {int(min_test_time%60)}s" if min_test_time >= 60 else f"{min_test_time:.1f}s"
        max_str = f"{int(max_test_time//60)}m {int(max_test_time%60)}s" if max_test_time >= 60 else f"{max_test_time:.1f}s"
        
        print("\n" + "=" * 80)
        print("BENCHMARKING STATISTICS")
        print("=" * 80)
        print(f"Total tests completed: {len(test_times)}")
        print(f"Total time: {benchmark_total_str}")
        print(f"Average time per test: {avg_str}")
        print(f"Fastest test: {min_str}")
        print(f"Slowest test: {max_str}")
        print("=" * 80)
        log_message("")
        log_message("=" * 80)
        log_message("BENCHMARKING STATISTICS")
        log_message("=" * 80)
        log_message(f"Total tests completed: {len(test_times)}")
        log_message(f"Total time: {benchmark_total_str}")
        log_message(f"Average time per test: {avg_str}")
        log_message(f"Fastest test: {min_str}")
        log_message(f"Slowest test: {max_str}")
        log_message("=" * 80)
    
    if completed_count > 0 or existing_results:
        resumed_tests = completed_count if completed_count > 0 else len(existing_results)
        print(f"\nResumed: {resumed_tests} test cases skipped (already completed)")
        log_message(f"Resumed: {resumed_tests} test cases skipped (already completed)")
        log_message("")
    
    # Step 3: Summary (results already saved incrementally)
    if all_results:
        print("\nSTEP 3: Results summary...")
        print("-" * 80)
        print(f"Results saved incrementally to: {output_file}\n")
        log_message("STEP 3: Results summary...")
        log_message("-" * 80)
        log_message(f"Results saved incrementally to: {output_file}")
        log_message("")
        
        # Print summary
        print("Summary:")
        print(f"{'Nodes':>10} {'DP-BU (ms)':>15} {'DP-TD (ms)':>15} "
              f"{'Graph-SS (ms)':>18} {'Graph-DAG (ms)':>18}")
        print("-" * 80)
        log_message("Summary:")
        log_message(f"{'Nodes':>10} {'DP-BU (ms)':>15} {'DP-TD (ms)':>15} "
                   f"{'Graph-SS (ms)':>18} {'Graph-DAG (ms)':>18}")
        log_message("-" * 80)
        
        # Sort results by actual_nodes (handle string 'N/A' and CSV string numbers gracefully)
        def get_node_count(result):
            nodes = result.get('actual_nodes', 'N/A')
            if nodes is None or nodes == 'N/A' or nodes == '':
                return 0  # Put N/A at the beginning
            try:
                # Convert string to int if needed (from CSV)
                return int(float(nodes)) if isinstance(nodes, str) else int(nodes)
            except (ValueError, TypeError):
                return 0  # Put invalid values at the beginning
        
        sorted_results = sorted(all_results, key=get_node_count)
        
        for result in sorted_results:
            nodes = result.get('actual_nodes', 'N/A')
            # Convert to string for display
            if isinstance(nodes, (int, float)):
                nodes_str = str(int(nodes))
            else:
                nodes_str = str(nodes)
            
            dp_bu = _format_result(result, 'dp_bottomup')
            dp_td = _format_result(result, 'dp_topdown')
            g_ss = _format_result(result, 'graph_statespace')
            g_dag = _format_result(result, 'graph_dag')
            
            print(f"{nodes_str:>10} {dp_bu:>15} {dp_td:>15} {g_ss:>18} {g_dag:>18}")
            log_message(f"{nodes_str:>10} {dp_bu:>15} {dp_td:>15} {g_ss:>18} {g_dag:>18}")
    
    # Step 4: Generate visualization graphs
    print("\nSTEP 4: Generating performance graphs...")
    print("-" * 80)
    log_message("")
    log_message("STEP 4: Generating performance graphs...")
    log_message("-" * 80)
    
    try:
        from visualize_results import load_benchmark_results, plot_runtime_vs_nodes, plot_runtime_vs_edges, plot_scalability_comparison
        
        results = load_benchmark_results(output_file)
        if results:
            print(f"Loaded {len(results)} benchmark results")
            log_message(f"Loaded {len(results)} benchmark results")
            plot_runtime_vs_nodes(results)
            print("  Generated: graphs/runtime_vs_nodes.png")
            log_message("  Generated: graphs/runtime_vs_nodes.png")
            plot_runtime_vs_edges(results)
            print("  Generated: graphs/runtime_vs_edges.png")
            log_message("  Generated: graphs/runtime_vs_edges.png")
            plot_scalability_comparison(results)
            print("  Generated: graphs/scalability_comparison.png")
            log_message("  Generated: graphs/scalability_comparison.png")
            print("All graphs generated successfully!")
            log_message("All graphs generated successfully!")
        else:
            print("Warning: No results to visualize")
            log_message("Warning: No results to visualize")
    except Exception as e:
        print(f"Warning: Could not generate graphs: {e}")
        print("You can generate them later with: python visualize_results.py")
        log_message(f"Warning: Could not generate graphs: {e}")
        log_message("You can generate them later with: python visualize_results.py")
    
    total_elapsed = time.perf_counter() - overall_start_time
    total_elapsed_str = f"{int(total_elapsed//3600):02d}:{int((total_elapsed%3600)//60):02d}:{int(total_elapsed%60):02d}"
    print("\n" + "=" * 80)
    print(f"Overnight benchmarking completed: {datetime.now()}")
    print(f"Total execution time: {total_elapsed_str}")
    print("=" * 80)
    log_message("")
    log_message("=" * 80)
    log_message(f"Overnight benchmarking completed: {datetime.now()}")
    log_message(f"Total execution time: {total_elapsed_str}")
    log_message("=" * 80)

def _format_result(result: Dict, solution_name: str) -> str:
    """Format result for display."""
    time_ms = result.get(f'{solution_name}_time')
    actual_time_ms = result.get(f'{solution_name}_actual_time')
    status = result.get(f'{solution_name}_status', 'N/A')
    
    # Convert to float if string (from CSV)
    try:
        if time_ms:
            time_ms = float(time_ms) if isinstance(time_ms, str) else time_ms
            # Convert to seconds or minutes if large
            if time_ms > 60000:  # > 1 minute
                return f"{time_ms/60000:.1f}m"
            elif time_ms > 1000:  # > 1 second
                return f"{time_ms/1000:.1f}s"
            else:
                return f"{time_ms:.0f}ms"
        elif actual_time_ms:
            actual_time_ms = float(actual_time_ms) if isinstance(actual_time_ms, str) else actual_time_ms
            if actual_time_ms > 60000:
                return f"{actual_time_ms/60000:.1f}m*"
            elif actual_time_ms > 1000:
                return f"{actual_time_ms/1000:.1f}s*"
            else:
                return f"{actual_time_ms:.0f}ms*"
    except (ValueError, TypeError):
        pass  # Fall through to return status
    
    return status[:15]

def main():
    """Main entry point."""
    # Default target sizes if not provided
    if len(sys.argv) > 1:
        target_sizes = [int(x) for x in sys.argv[1:]]
    else:
        # Progressive sizes for overnight run
        target_sizes = [500, 1000, 2000, 5000, 10000, 20000, 50000, 100000]
    
    print("=" * 80)
    print("Overnight Benchmarking Script")
    print("=" * 80)
    print("This script will:")
    print("  1. Generate test cases (if needed)")
    print("  2. Run benchmarks with NO TIMEOUT (ALL 4 solutions)")
    print("  3. Save all results to CSV (incremental)")
    print("  4. Generate performance graphs")
    print("  5. Log everything to overnight_log.txt")
    print("")
    print(f"Target sizes: {target_sizes}")
    print("")
    print("Memory optimizations:")
    print("  - Incremental CSV writing (no memory buildup)")
    print("  - Garbage collection after each test case")
    print("  - Graph solutions skipped for sizes >= 5,000 nodes")
    print("  - DP solutions (bottom-up & top-down) run for all sizes")
    print("")
    print("Press Ctrl+C to stop at any time")
    print("=" * 80)
    print()
    
    try:
        # Run with graph solutions skipped for sizes >= 5,000 nodes
        # DP solutions (bottom-up & top-down) run for all sizes
        run_overnight_benchmark(target_sizes, skip_graph_solutions_for_large=5000)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Partial results may be saved.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

