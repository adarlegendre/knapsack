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
        tolerance: Acceptable deviation from target (±10% default, relaxed for large sizes)
        
    Returns:
        Dictionary with 'items', 'capacity', 'actual_nodes', 'actual_edges', 'error'
    """
    if target_edges is None:
        # Estimate edges: roughly 2-5x nodes depending on items
        target_edges = int(target_nodes * 3)
    
    # Relax tolerance for very large sizes (it's hard to hit exact targets)
    if target_nodes >= 30000:
        tolerance = 0.3  # 30% tolerance for 30K+
    elif target_nodes >= 20000:
        tolerance = 0.25  # 25% tolerance for 20K+
    elif target_nodes >= 10000:
        tolerance = 0.2  # 20% tolerance for 10K+
    
    best_case = None
    best_error = float('inf')
    
    # Improved heuristics for very large sizes
    # For large sizes, we need more items with smaller weights to create more states
    if target_nodes < 1000:
        num_items_range = (8, 15)
        weight_range = (1, 10)
    elif target_nodes < 5000:
        num_items_range = (12, 20)
        weight_range = (1, 15)
    elif target_nodes < 20000:
        num_items_range = (15, 25)
        weight_range = (1, 20)
    elif target_nodes < 50000:
        num_items_range = (18, 28)
        weight_range = (1, 18)  # Smaller weights for more states
    elif target_nodes < 100000:
        num_items_range = (20, 30)
        weight_range = (1, 15)  # Even smaller weights
    else:  # 100K+
        num_items_range = (22, 32)
        weight_range = (1, 12)  # Smallest weights for maximum states
    
    # Reduce capacity ratios to try (fewer iterations for large sizes)
    if target_nodes >= 50000:
        capacity_ratios = [0.55, 0.65]  # Just 2 ratios for very large
    elif target_nodes >= 20000:
        capacity_ratios = [0.5, 0.6, 0.7]  # 3 ratios
    elif target_nodes > 5000:
        capacity_ratios = [0.5, 0.6, 0.7]
    else:
        capacity_ratios = [0.4, 0.5, 0.6, 0.7, 0.8]
    
    # For very large sizes, use adaptive search strategy
    adaptive_search = target_nodes >= 20000
    
    for attempt in range(max_attempts):
        # Try different parameter combinations
        num_items = random.randint(num_items_range[0], num_items_range[1])
        weight_min, weight_max = weight_range
        value_min, value_max = (1, weight_max * 2)  # Values typically 1-2x weights
        
        # Adaptive adjustments based on attempt number and target size
        if adaptive_search:
            # For large sizes, progressively try smaller weights
            if attempt < max_attempts // 3:
                # First third: try current range
                pass
            elif attempt < 2 * max_attempts // 3:
                # Second third: reduce weights slightly
                weight_max = max(weight_min, weight_max - 2)
            else:
                # Last third: reduce weights more aggressively
                weight_max = max(weight_min, weight_max - 4)
        else:
            # Original strategy for smaller sizes
            if attempt > max_attempts // 2:
                weight_max = max(weight_min, weight_max - 3)
        
        items = generate_items(num_items, (weight_min, weight_max), 
                              (value_min, value_max), seed=attempt)
        
        # Try different capacity ratios (reduced for large targets)
        for ratio in capacity_ratios:
            capacity = estimate_capacity(items, ratio)
            if capacity < 1:
                continue
            
            try:
                # Early termination: if we're way off target, skip early
                # Use larger limit for very large sizes to allow more exploration
                # For very large sizes, be more lenient to allow finding ANY valid case
                if target_nodes >= 50000:
                    max_nodes_limit = int(target_nodes * 4.0)  # Very lenient for 50K+
                elif target_nodes >= 30000:
                    max_nodes_limit = int(target_nodes * 3.5)  # More lenient for 30K+
                elif target_nodes >= 20000:
                    max_nodes_limit = int(target_nodes * 3.0)  # More lenient for 20K+
                elif target_nodes > 1000:
                    max_nodes_limit = int(target_nodes * 2.5)
                else:
                    max_nodes_limit = None
                    
                actual_nodes, actual_edges = count_graph_nodes_edges(items, capacity, max_nodes=max_nodes_limit)
                
                # If we hit the limit, this case is too large, skip it
                # BUT for very large sizes, accept cases that are close to limit if we have no better option
                if max_nodes_limit and actual_nodes >= max_nodes_limit:
                    # For very large sizes, if we have no best_case yet, accept this one
                    if target_nodes >= 20000 and best_case is None:
                        # Accept this as best_case even if over limit (better than nothing)
                        # Use actual error instead of 1.0
                        node_error = abs(actual_nodes - target_nodes) / target_nodes
                        best_case = {
                            'items': items,
                            'capacity': capacity,
                            'actual_nodes': actual_nodes,
                            'actual_edges': actual_edges,
                            'target_nodes': target_nodes,
                            'target_edges': target_edges,
                            'error': node_error,  # Use actual error
                            'num_items': num_items
                        }
                        best_error = node_error
                    continue
                
                # Skip if actual_nodes is 0 (invalid case)
                if actual_nodes == 0:
                    continue
                
                # Calculate error (normalized)
                node_error = abs(actual_nodes - target_nodes) / target_nodes
                edge_error = abs(actual_edges - target_edges) / target_edges if target_edges > 0 else 0
                total_error = (node_error + edge_error) / 2
                
                # For very large sizes, prioritize node count over edge count
                if target_nodes >= 30000:
                    total_error = node_error * 0.8 + edge_error * 0.2
                
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
                # Skip if error (e.g., too large, memory error)
                # For debugging: log first few errors for large sizes
                if target_nodes >= 20000 and attempt < 3:
                    import sys
                    print(f"      Attempt {attempt+1}: Exception - {type(e).__name__}: {str(e)[:100]}", file=sys.stderr)
                continue
    
    # Return best case found (even if not within tolerance)
    if best_case:
        return best_case
    
    # If no best case found, try one more time with very conservative parameters
    # This is a fallback for very large sizes
    if target_nodes >= 20000:
        print(f"    Warning: No good match found, trying fallback strategy...")
        # Try with minimal items and weights to maximize states
        fallback_items = generate_items(
            num_items_range[0],  # Minimum items
            (1, weight_range[1] // 2),  # Half the max weight
            (1, weight_range[1]),  # Values
            seed=999999  # Fixed seed for reproducibility
        )
        
        # Try a few capacity ratios
        for ratio in [0.5, 0.6]:
            try:
                capacity = estimate_capacity(fallback_items, ratio)
                if capacity < 1:
                    continue
                
                # Very lenient limit for fallback
                max_nodes_limit = int(target_nodes * 5.0)
                actual_nodes, actual_edges = count_graph_nodes_edges(
                    fallback_items, capacity, max_nodes=max_nodes_limit
                )
                
                # Accept any valid case as fallback
                if actual_nodes > 0:
                    return {
                        'items': fallback_items,
                        'capacity': capacity,
                        'actual_nodes': actual_nodes,
                        'actual_edges': actual_edges,
                        'target_nodes': target_nodes,
                        'target_edges': target_edges,
                        'error': abs(actual_nodes - target_nodes) / target_nodes,
                        'num_items': len(fallback_items)
                    }
            except Exception:
                continue
    
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

