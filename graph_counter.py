"""
Graph Counter Utility
Counts the number of nodes (states) and edges (transitions) in the state-space graph
for a given knapsack problem instance.

This implements Option 2: State-space graph representation where:
- Nodes = states (current_weight, items_selected)
- Edges = transitions (adding one item)
- Edge weights = value gained by adding the item
"""

import json
from typing import List, Dict, Tuple
from collections import deque, defaultdict

def count_graph_nodes_edges(items: List[Dict], capacity: int, max_nodes: int = None) -> Tuple[int, int]:
    """
    Count the number of nodes and edges in the state-space graph.
    Optimized: Early termination, efficient state representation.
    
    Args:
        items: List of items with 'name', 'weight', 'value'
        capacity: Maximum weight capacity
        max_nodes: Optional limit - stop counting if exceeds this (for early termination)
        
    Returns:
        Tuple of (num_nodes, num_edges)
    """
    # Pre-extract item properties for faster access
    item_weights = [item['weight'] for item in items]
    item_names = [item['name'] for item in items]
    n = len(items)
    
    # Use frozenset for items (faster than tuple for membership testing)
    # But we'll use a bitmask approach for even better performance
    # State: (weight, items_bitmask) where bitmask is an integer
    
    nodes = set()
    edges = 0
    visited = set()
    
    # Start with empty knapsack state: weight=0, no items (bitmask=0)
    start = (0, 0)
    nodes.add(start)
    queue = deque([start])
    visited.add(start)
    
    while queue:
        current_weight, items_mask = queue.popleft()
        
        # Early termination if we exceed max_nodes limit
        # Check before processing to avoid unnecessary work
        if max_nodes is not None and len(nodes) >= max_nodes:
            return len(nodes), edges
        
        # Try adding each item not yet selected
        for i in range(n):
            # Check if item i is already selected (using bitmask)
            if items_mask & (1 << i):
                continue
            
            weight = item_weights[i]
            new_weight = current_weight + weight
            
            if new_weight <= capacity:
                # Create new state with item i added
                new_mask = items_mask | (1 << i)
                new_state = (new_weight, new_mask)
                
                edges += 1  # Count edge
                
                if new_state not in visited:
                    visited.add(new_state)
                    nodes.add(new_state)
                    queue.append(new_state)
    
    return len(nodes), edges

def count_graph_metrics(input_file: str = 'input.json') -> Dict:
    """
    Count graph metrics for a given input file.
    
    Args:
        input_file: Path to JSON input file
        
    Returns:
        Dictionary with metrics: nodes, edges, num_items, capacity
    """
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    items = data['items']
    capacity = data['capacity']
    
    num_nodes, num_edges = count_graph_nodes_edges(items, capacity)
    
    return {
        'nodes': num_nodes,
        'edges': num_edges,
        'num_items': len(items),
        'capacity': capacity,
        'avg_weight': sum(item['weight'] for item in items) / len(items) if items else 0,
        'avg_value': sum(item['value'] for item in items) / len(items) if items else 0
    }

def main():
    """CLI interface for graph counter."""
    import sys
    
    input_file = sys.argv[1] if len(sys.argv) > 1 else 'input.json'
    
    try:
        metrics = count_graph_metrics(input_file)
        print(f"Graph Metrics for {input_file}:")
        print(f"  Nodes (states): {metrics['nodes']}")
        print(f"  Edges (transitions): {metrics['edges']}")
        print(f"  Number of items: {metrics['num_items']}")
        print(f"  Capacity: {metrics['capacity']}")
        print(f"  Average weight: {metrics['avg_weight']:.2f}")
        print(f"  Average value: {metrics['avg_value']:.2f}")
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

