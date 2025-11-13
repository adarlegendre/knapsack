"""
Performance Visualization
Generates performance graphs from benchmark results.

Creates visualizations comparing runtime across different graph sizes for all solutions.
"""

import csv
import matplotlib.pyplot as plt
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
                       'graph_statespace_time', 'graph_dag_time']:
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
    Filter results where a solution succeeded.
    
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
        status_key = f'{solution_name}_status'
        
        if (result.get(time_key) is not None and 
            result.get(status_key) == 'SUCCESS' and
            result.get('actual_nodes') is not None):
            nodes.append(result['actual_nodes'])
            edges.append(result.get('actual_edges', 0))
            times.append(result[time_key])
    
    return nodes, edges, times

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
    
    for sol_name, sol_label, color, linestyle in solutions:
        nodes, _, times = filter_valid_results(results, sol_name)
        
        if nodes and times:
            # Sort by nodes
            sorted_data = sorted(zip(nodes, times))
            nodes_sorted, times_sorted = zip(*sorted_data)
            
            plt.plot(nodes_sorted, times_sorted, label=sol_label, 
                    color=color, linestyle=linestyle, marker='o', markersize=4, linewidth=2)
    
    plt.xlabel('Number of Nodes (States)', fontsize=12)
    plt.ylabel('Runtime (milliseconds)', fontsize=12)
    plt.title('Knapsack Solution Performance: Runtime vs Graph Size (Nodes)', fontsize=14, fontweight='bold')
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.xscale('log')
    plt.yscale('log')
    
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
    
    for sol_name, sol_label, color, linestyle in solutions:
        _, edges, times = filter_valid_results(results, sol_name)
        
        if edges and times:
            # Sort by edges
            sorted_data = sorted(zip(edges, times))
            edges_sorted, times_sorted = zip(*sorted_data)
            
            plt.plot(edges_sorted, times_sorted, label=sol_label, 
                    color=color, linestyle=linestyle, marker='o', markersize=4, linewidth=2)
    
    plt.xlabel('Number of Edges (Transitions)', fontsize=12)
    plt.ylabel('Runtime (milliseconds)', fontsize=12)
    plt.title('Knapsack Solution Performance: Runtime vs Graph Size (Edges)', fontsize=14, fontweight='bold')
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.xscale('log')
    plt.yscale('log')
    
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
    for sol_name, sol_label, color in solutions:
        nodes, _, times = filter_valid_results(results, sol_name)
        
        if nodes and times:
            sorted_data = sorted(zip(nodes, times))
            nodes_sorted, times_sorted = zip(*sorted_data)
            ax1.plot(nodes_sorted, times_sorted, label=sol_label, 
                    color=color, marker='o', markersize=4, linewidth=2)
    
    ax1.set_xlabel('Number of Nodes', fontsize=11)
    ax1.set_ylabel('Runtime (ms)', fontsize=11)
    ax1.set_title('Runtime vs Nodes', fontsize=12, fontweight='bold')
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    
    # Plot 2: Runtime vs Edges
    for sol_name, sol_label, color in solutions:
        _, edges, times = filter_valid_results(results, sol_name)
        
        if edges and times:
            sorted_data = sorted(zip(edges, times))
            edges_sorted, times_sorted = zip(*sorted_data)
            ax2.plot(edges_sorted, times_sorted, label=sol_label, 
                    color=color, marker='o', markersize=4, linewidth=2)
    
    ax2.set_xlabel('Number of Edges', fontsize=11)
    ax2.set_ylabel('Runtime (ms)', fontsize=11)
    ax2.set_title('Runtime vs Edges', fontsize=12, fontweight='bold')
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)
    ax2.set_xscale('log')
    ax2.set_yscale('log')
    
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

