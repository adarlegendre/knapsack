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

def count_graph_nodes_edges(items: List[Dict], capacity: int) -> Tuple[int, int]:
    """
    Count the number of nodes and edges in the state-space graph.
    
    Args:
        items: List of items with 'name', 'weight', 'value'
        capacity: Maximum weight capacity
        
    Returns:
        Tuple of (num_nodes, num_edges)
    """
    # Build the state-space graph
    graph = defaultdict(list)  # node -> [(neighbor, edge_weight), ...]
    nodes = set()
    
    # Start with empty knapsack state
    start = (0, ())
    nodes.add(start)
    queue = deque([start])
    visited = set()
    
    while queue:
        current_state = queue.popleft()
        if current_state in visited:
            continue
        visited.add(current_state)
        
        current_weight, current_items = current_state
        
        # Try adding each item not yet selected
        for item in items:
            if item['name'] in current_items:
                continue
            
            new_weight = current_weight + item['weight']
            if new_weight <= capacity:
                # Create new state
                new_items = tuple(sorted(current_items + (item['name'],)))
                new_state = (new_weight, new_items)
                
                # Add edge from current_state to new_state
                graph[current_state].append((new_state, item['value']))
                nodes.add(new_state)
                
                if new_state not in visited:
                    queue.append(new_state)
    
    # Count edges
    num_edges = sum(len(neighbors) for neighbors in graph.values())
    num_nodes = len(nodes)
    
    return num_nodes, num_edges

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

