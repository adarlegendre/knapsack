"""
Test Case Generator
Generates knapsack problem instances that target specific graph sizes (nodes and edges).

Uses iterative refinement to find input parameters (items, weights, capacity) that
produce state-space graphs close to the target number of nodes and edges.
"""

import json
import random
import math
from typing import List, Dict, Tuple
from graph_counter import count_graph_nodes_edges

def generate_items(num_items: int, weight_range: Tuple[int, int], 
                   value_range: Tuple[int, int], seed: int = None) -> List[Dict]:
    """
    Generate random items.
    
    Args:
        num_items: Number of items to generate
        weight_range: (min_weight, max_weight)
        value_range: (min_value, max_value)
        seed: Random seed for reproducibility
        
    Returns:
        List of items with 'name', 'weight', 'value'
    """
    if seed is not None:
        random.seed(seed)
    
    items = []
    for i in range(num_items):
        weight = random.randint(weight_range[0], weight_range[1])
        value = random.randint(value_range[0], value_range[1])
        items.append({
            'name': f'Item_{i+1}',
            'weight': weight,
            'value': value
        })
    
    return items

def estimate_capacity(items: List[Dict], target_ratio: float = 0.6) -> int:
    """
    Estimate capacity based on items and target ratio.
    
    Args:
        items: List of items
        target_ratio: Ratio of total weight to use as capacity (0.6 = 60%)
        
    Returns:
        Estimated capacity
    """
    total_weight = sum(item['weight'] for item in items)
    return int(total_weight * target_ratio)

def find_closest_test_case(target_nodes: int, target_edges: int = None,
                          max_attempts: int = 50, tolerance: float = 0.1) -> Dict:
    """
    Find test case parameters that produce graph close to target size.
    
    Args:
        target_nodes: Target number of nodes
        target_edges: Target number of edges (if None, will be estimated)
        max_attempts: Maximum attempts to find good parameters
        tolerance: Acceptable deviation from target (±10% default)
        
    Returns:
        Dictionary with 'items', 'capacity', 'actual_nodes', 'actual_edges', 'error'
    """
    if target_edges is None:
        # Estimate edges: roughly 2-5x nodes depending on items
        target_edges = int(target_nodes * 3)
    
    best_case = None
    best_error = float('inf')
    
    # Heuristics for initial parameters
    # More nodes typically need more items, but relationship is exponential
    if target_nodes < 1000:
        num_items_range = (8, 15)
        weight_range = (1, 10)
    elif target_nodes < 5000:
        num_items_range = (12, 20)
        weight_range = (1, 15)
    elif target_nodes < 20000:
        num_items_range = (15, 25)
        weight_range = (1, 20)
    else:
        num_items_range = (18, 30)
        weight_range = (1, 25)
    
    for attempt in range(max_attempts):
        # Try different parameter combinations
        num_items = random.randint(num_items_range[0], num_items_range[1])
        weight_min, weight_max = weight_range
        value_min, value_max = (1, weight_max * 2)  # Values typically 1-2x weights
        
        # Adjust based on attempt number
        if attempt > max_attempts // 2:
            # Try smaller weights to get more states
            weight_max = max(weight_min, weight_max - 3)
        
        items = generate_items(num_items, (weight_min, weight_max), 
                              (value_min, value_max), seed=attempt)
        
        # Try different capacity ratios
        for ratio in [0.4, 0.5, 0.6, 0.7, 0.8]:
            capacity = estimate_capacity(items, ratio)
            if capacity < 1:
                continue
            
            try:
                actual_nodes, actual_edges = count_graph_nodes_edges(items, capacity)
                
                # Calculate error (normalized)
                node_error = abs(actual_nodes - target_nodes) / target_nodes
                edge_error = abs(actual_edges - target_edges) / target_edges if target_edges > 0 else 0
                total_error = (node_error + edge_error) / 2
                
                # Check if within tolerance
                if node_error <= tolerance and edge_error <= tolerance:
                    return {
                        'items': items,
                        'capacity': capacity,
                        'actual_nodes': actual_nodes,
                        'actual_edges': actual_edges,
                        'target_nodes': target_nodes,
                        'target_edges': target_edges,
                        'error': total_error,
                        'num_items': num_items
                    }
                
                # Track best so far
                if total_error < best_error:
                    best_error = total_error
                    best_case = {
                        'items': items,
                        'capacity': capacity,
                        'actual_nodes': actual_nodes,
                        'actual_edges': actual_edges,
                        'target_nodes': target_nodes,
                        'target_edges': target_edges,
                        'error': total_error,
                        'num_items': num_items
                    }
            except Exception as e:
                # Skip if error (e.g., too large)
                continue
    
    # Return best case found (even if not within tolerance)
    if best_case:
        return best_case
    else:
        raise ValueError(f"Could not generate test case for target {target_nodes} nodes")

def generate_test_cases(target_sizes: List[int], output_dir: str = 'results') -> List[Dict]:
    """
    Generate multiple test cases for different target sizes.
    
    Args:
        target_sizes: List of target node counts
        output_dir: Directory to save test case files
        
    Returns:
        List of test case info dictionaries
    """
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    test_cases = []
    
    for target_nodes in target_sizes:
        print(f"Generating test case for {target_nodes} nodes...")
        
        try:
            test_case = find_closest_test_case(target_nodes)
            
            # Save to file
            filename = f"{output_dir}/test_{target_nodes}.json"
            output_data = {
                'capacity': test_case['capacity'],
                'items': test_case['items'],
                'metadata': {
                    'target_nodes': target_nodes,
                    'actual_nodes': test_case['actual_nodes'],
                    'actual_edges': test_case['actual_edges'],
                    'num_items': test_case['num_items'],
                    'error': test_case['error']
                }
            }
            
            with open(filename, 'w') as f:
                json.dump(output_data, f, indent=2)
            
            test_cases.append({
                'filename': filename,
                'target_nodes': target_nodes,
                'actual_nodes': test_case['actual_nodes'],
                'actual_edges': test_case['actual_edges'],
                'error': test_case['error']
            })
            
            print(f"  [OK] Generated: {filename}")
            print(f"    Actual: {test_case['actual_nodes']} nodes, {test_case['actual_edges']} edges")
            print(f"    Error: {test_case['error']*100:.1f}%")
        except Exception as e:
            print(f"  [FAILED] {e}")
            test_cases.append({
                'filename': None,
                'target_nodes': target_nodes,
                'error': str(e)
            })
    
    return test_cases

def main():
    """CLI interface for test generator."""
    import sys
    
    # Default target sizes
    default_sizes = [500, 1000, 1500, 2000, 2500, 5000, 7500, 10000, 
                     15000, 20000, 25000, 30000, 50000, 75000, 100000]
    
    if len(sys.argv) > 1:
        # Custom sizes from command line
        target_sizes = [int(x) for x in sys.argv[1:]]
    else:
        target_sizes = default_sizes
    
    print("=" * 60)
    print("Test Case Generator")
    print("=" * 60)
    print(f"Generating test cases for target sizes: {target_sizes}")
    print()
    
    test_cases = generate_test_cases(target_sizes)
    
    print()
    print("=" * 60)
    print("Summary:")
    print("=" * 60)
    for tc in test_cases:
        if tc['filename']:
            print(f"  {tc['target_nodes']:6d} nodes → {tc['actual_nodes']:6d} nodes, "
                  f"{tc['actual_edges']:6d} edges (error: {tc['error']*100:.1f}%)")
        else:
            print(f"  {tc['target_nodes']:6d} nodes → FAILED")

if __name__ == "__main__":
    main()

