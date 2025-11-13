"""
Knapsack Problem - DAG Longest Path Solution
Uses Option 2: State-space graph representation
Nodes = states (current_weight, items_selected)
Edge weights = value gained by adding an item
Finds longest path in DAG (maximize value)
"""

import json
import time
from typing import List, Dict, Tuple, Set
from collections import defaultdict, deque

def knapsack_graph_dag(items: List[Dict], capacity: int) -> Tuple[int, List[str]]:
    """
    Solve 0/1 knapsack by modeling as DAG and finding longest path.
    
    Args:
        items: List of items with 'name', 'weight', 'value'
        capacity: Maximum weight capacity
        
    Returns:
        Tuple of (max_value, selected_items)
    """
    # Build DAG: nodes are states, edges have weights (values)
    # State representation: (weight, items_tuple)
    graph = defaultdict(list)  # node -> [(neighbor, edge_weight), ...]
    in_degree = defaultdict(int)
    
    # Initialize: start node (0, ())
    start = (0, ())
    nodes = {start}
    
    # Build graph by exploring all reachable states
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
                new_items = tuple(sorted(current_items + (item['name'],)))
                new_state = (new_weight, new_items)
                
                # Add edge with weight = item value
                graph[current_state].append((new_state, item['value']))
                in_degree[new_state] += 1
                
                if new_state not in visited:
                    queue.append(new_state)
                    nodes.add(new_state)
    
    # Topological sort (all edges go from lower to higher weight, so BFS order works)
    # Longest path in DAG using dynamic programming
    dist = {node: (0, []) for node in nodes}  # (max_value, path_items)
    dist[start] = (0, [])
    
    # Process nodes in topological order (BFS from start)
    queue = deque([start])
    processed = set()
    
    while queue:
        u = queue.popleft()
        if u in processed:
            continue
        processed.add(u)
        
        for v, edge_weight in graph[u]:
            new_value = dist[u][0] + edge_weight
            if new_value > dist[v][0]:
                # Get items from state v
                _, items_tuple = v
                dist[v] = (new_value, list(items_tuple))
            
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)
    
    # Find node with maximum value
    best_node = max(dist.items(), key=lambda x: x[1][0])
    return best_node[1][0], best_node[1][1]

def main():
    # Read input
    with open('input.json', 'r') as f:
        data = json.load(f)
    
    items = data['items']
    capacity = data['capacity']
    
    print("=" * 60)
    print("DAG Longest Path Solution (State-Space Graph - Option 2)")
    print("=" * 60)
    print(f"Capacity: {capacity}")
    print(f"Items: {len(items)}")
    print("\nItems:")
    for item in items:
        print(f"  {item['name']}: weight={item['weight']}, value={item['value']}")
    print()
    
    # Solve and time
    start_time = time.perf_counter()
    max_value, selected_items = knapsack_graph_dag(items, capacity)
    end_time = time.perf_counter()
    execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
    
    # Output results
    print("Results:")
    print(f"  Selected items: {selected_items}")
    print(f"  Total value: {max_value}")
    print(f"  Execution time: {execution_time:.4f} ms")
    print("=" * 60)

if __name__ == "__main__":
    main()

