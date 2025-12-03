"""
Performance Visualization
Generates performance graphs from benchmark results.

Creates visualizations comparing runtime across different graph sizes for all solutions.
"""

import csv
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import os
from typing import List, Dict, Optional

def load_benchmark_results(csv_file: str = 'results/benchmark_results.csv') -> List[Dict]:
    """
    Load benchmark results from CSV file.
    
    Args:
        csv_file: Path to CSV file
        
    Returns:
        List of result dictionaries
    """
    results = []
    
    if not os.path.exists(csv_file):
        print(f"Error: Benchmark results file '{csv_file}' not found.")
        print("Run benchmark.py first to generate results.")
        return results
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert numeric fields
            for key in ['target_nodes', 'actual_nodes', 'actual_edges', 
                       'num_items', 'capacity',
                       'dp_bottomup_time', 'dp_topdown_time',
                       'graph_statespace_time', 'graph_dag_time',
                       'dp_bottomup_actual_time', 'dp_topdown_actual_time',
                       'graph_statespace_actual_time', 'graph_dag_actual_time']:
                if key in row and row[key] and row[key] != 'N/A':
                    try:
                        row[key] = float(row[key])
                    except ValueError:
                        row[key] = None
                else:
                    row[key] = None
            
            results.append(row)
    
    return results

def filter_valid_results(results: List[Dict], solution_name: str) -> tuple:
    """
    Filter results where a solution has valid runtime data.
    Uses actual_time_ms as fallback when time_ms is None (for timeouts/errors).
    
    Args:
        results: List of result dictionaries
        solution_name: Name of solution (e.g., 'dp_bottomup')
        
    Returns:
        Tuple of (nodes_list, edges_list, times_list)
    """
    nodes = []
    edges = []
    times = []
    
    for result in results:
        time_key = f'{solution_name}_time'
        actual_time_key = f'{solution_name}_actual_time'
        status_key = f'{solution_name}_status'
        
        # Use time_ms if available, otherwise fall back to actual_time_ms
        # This ensures we show actual runtime even for timeouts
        runtime_ms = result.get(time_key)
        if runtime_ms is None:
            runtime_ms = result.get(actual_time_key)
        
        # Include result if we have valid runtime and nodes
        if (runtime_ms is not None and 
            result.get('actual_nodes') is not None):
            nodes.append(result['actual_nodes'])
            edges.append(result.get('actual_edges', 0))
            times.append(runtime_ms)
    
    return nodes, edges, times

def format_time_axis(value, pos):
    """Format time axis labels (ms, s, or min)."""
    if value >= 60000:  # >= 1 minute
        return f'{value/60000:.1f}m'
    elif value >= 1000:  # >= 1 second
        return f'{value/1000:.1f}s'
    else:
        return f'{value:.0f}ms'

def should_use_log_scale(times: List[float]) -> bool:
    """Determine if log scale is appropriate based on data range."""
    if not times or len(times) < 2:
        return False
    min_time = min(times)
    max_time = max(times)
    if min_time <= 0:
        return False
    # Use log scale if range spans more than 2 orders of magnitude
    ratio = max_time / min_time
    return ratio > 100

def plot_runtime_vs_nodes(results: List[Dict], output_file: str = 'graphs/runtime_vs_nodes.png'):
    """
    Plot runtime vs number of nodes for all solutions.
    
    Args:
        results: List of benchmark results
        output_file: Output file path
    """
    plt.figure(figsize=(12, 8))
    
    solutions = [
        ('dp_bottomup', 'DP Bottom-Up', 'blue', '-'),
        ('dp_topdown', 'DP Top-Down', 'green', '--'),
        ('graph_statespace', 'Graph State-Space', 'red', '-.'),
        ('graph_dag', 'Graph DAG', 'orange', ':')
    ]
    
    all_times = []
    for sol_name, sol_label, color, linestyle in solutions:
        nodes, _, times = filter_valid_results(results, sol_name)
        
        if nodes and times:
            # Sort by nodes
            sorted_data = sorted(zip(nodes, times))
            nodes_sorted, times_sorted = zip(*sorted_data)
            all_times.extend(times)
            
            plt.plot(nodes_sorted, times_sorted, label=sol_label, 
                    color=color, linestyle=linestyle, marker='o', markersize=4, linewidth=2)
    
    plt.xlabel('Number of Nodes (States)', fontsize=12)
    plt.ylabel('Runtime', fontsize=12)
    plt.title('Knapsack Solution Performance: Runtime vs Graph Size (Nodes)\n(Shows actual runtime, including timeouts)', fontsize=14, fontweight='bold')
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.xscale('log')
    
    # Use log scale for y-axis if data spans wide range, otherwise linear
    if all_times and should_use_log_scale(all_times):
        plt.yscale('log')
        # For log scale, use standard formatter
        plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: format_time_axis(x, p)))
    else:
        # For linear scale, use custom formatter
        plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(format_time_axis))
    
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_file}")

def plot_runtime_vs_edges(results: List[Dict], output_file: str = 'graphs/runtime_vs_edges.png'):
    """
    Plot runtime vs number of edges for all solutions.
    
    Args:
        results: List of benchmark results
        output_file: Output file path
    """
    plt.figure(figsize=(12, 8))
    
    solutions = [
        ('dp_bottomup', 'DP Bottom-Up', 'blue', '-'),
        ('dp_topdown', 'DP Top-Down', 'green', '--'),
        ('graph_statespace', 'Graph State-Space', 'red', '-.'),
        ('graph_dag', 'Graph DAG', 'orange', ':')
    ]
    
    all_times = []
    for sol_name, sol_label, color, linestyle in solutions:
        _, edges, times = filter_valid_results(results, sol_name)
        
        if edges and times:
            # Sort by edges
            sorted_data = sorted(zip(edges, times))
            edges_sorted, times_sorted = zip(*sorted_data)
            all_times.extend(times)
            
            plt.plot(edges_sorted, times_sorted, label=sol_label, 
                    color=color, linestyle=linestyle, marker='o', markersize=4, linewidth=2)
    
    plt.xlabel('Number of Edges (Transitions)', fontsize=12)
    plt.ylabel('Runtime', fontsize=12)
    plt.title('Knapsack Solution Performance: Runtime vs Graph Size (Edges)\n(Shows actual runtime, including timeouts)', fontsize=14, fontweight='bold')
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.xscale('log')
    
    # Use log scale for y-axis if data spans wide range, otherwise linear
    if all_times and should_use_log_scale(all_times):
        plt.yscale('log')
        plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: format_time_axis(x, p)))
    else:
        plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(format_time_axis))
    
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_file}")

def plot_scalability_comparison(results: List[Dict], output_file: str = 'graphs/scalability_comparison.png'):
    """
    Plot scalability comparison showing which solutions work at different scales.
    
    Args:
        results: List of benchmark results
        output_file: Output file path
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    solutions = [
        ('dp_bottomup', 'DP Bottom-Up', 'blue'),
        ('dp_topdown', 'DP Top-Down', 'green'),
        ('graph_statespace', 'Graph State-Space', 'red'),
        ('graph_dag', 'Graph DAG', 'orange')
    ]
    
    # Plot 1: Runtime vs Nodes
    all_times_1 = []
    for sol_name, sol_label, color in solutions:
        nodes, _, times = filter_valid_results(results, sol_name)
        
        if nodes and times:
            sorted_data = sorted(zip(nodes, times))
            nodes_sorted, times_sorted = zip(*sorted_data)
            all_times_1.extend(times)
            ax1.plot(nodes_sorted, times_sorted, label=sol_label, 
                    color=color, marker='o', markersize=4, linewidth=2)
    
    ax1.set_xlabel('Number of Nodes', fontsize=11)
    ax1.set_ylabel('Runtime', fontsize=11)
    ax1.set_title('Runtime vs Nodes', fontsize=12, fontweight='bold')
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)
    ax1.set_xscale('log')
    if all_times_1 and should_use_log_scale(all_times_1):
        ax1.set_yscale('log')
        ax1.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: format_time_axis(x, p)))
    else:
        ax1.yaxis.set_major_formatter(ticker.FuncFormatter(format_time_axis))
    
    # Plot 2: Runtime vs Edges
    all_times_2 = []
    for sol_name, sol_label, color in solutions:
        _, edges, times = filter_valid_results(results, sol_name)
        
        if edges and times:
            sorted_data = sorted(zip(edges, times))
            edges_sorted, times_sorted = zip(*sorted_data)
            all_times_2.extend(times)
            ax2.plot(edges_sorted, times_sorted, label=sol_label, 
                    color=color, marker='o', markersize=4, linewidth=2)
    
    ax2.set_xlabel('Number of Edges', fontsize=11)
    ax2.set_ylabel('Runtime', fontsize=11)
    ax2.set_title('Runtime vs Edges', fontsize=12, fontweight='bold')
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)
    ax2.set_xscale('log')
    if all_times_2 and should_use_log_scale(all_times_2):
        ax2.set_yscale('log')
        ax2.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: format_time_axis(x, p)))
    else:
        ax2.yaxis.set_major_formatter(ticker.FuncFormatter(format_time_axis))
    
    plt.suptitle('Knapsack Solutions: Scalability Comparison', fontsize=14, fontweight='bold')
    
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_file}")

def generate_all_graphs(csv_file: str = 'results/benchmark_results.csv'):
    """
    Generate all performance graphs.
    
    Args:
        csv_file: Path to benchmark results CSV
    """
    print("=" * 80)
    print("Generating Performance Graphs")
    print("=" * 80)
    
    results = load_benchmark_results(csv_file)
    
    if not results:
        return
    
    print(f"Loaded {len(results)} benchmark results")
    print()
    
    # Generate graphs
    plot_runtime_vs_nodes(results)
    plot_runtime_vs_edges(results)
    plot_scalability_comparison(results)
    
    print()
    print("=" * 80)
    print("All graphs generated successfully!")
    print("=" * 80)

def main():
    """CLI interface for visualization."""
    import sys
    
    csv_file = sys.argv[1] if len(sys.argv) > 1 else 'results/benchmark_results.csv'
    generate_all_graphs(csv_file)

if __name__ == "__main__":
    main()

