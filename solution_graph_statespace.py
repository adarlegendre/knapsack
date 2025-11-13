"""
Knapsack Problem - Graph-Based State-Space Traversal Solution
Uses Option 2: State-space graph representation
Nodes = states (current_weight, items_selected)
Edge weights = value gained by adding an item
"""

import json
import time
from typing import List, Dict, Tuple, Set
from collections import deque

def knapsack_graph_statespace(items: List[Dict], capacity: int) -> Tuple[int, List[str]]:
    """
    Solve 0/1 knapsack by explicitly building and traversing state-space graph.
    
    Args:
        items: List of items with 'name', 'weight', 'value'
        capacity: Maximum weight capacity
        
    Returns:
        Tuple of (max_value, selected_items)
    """
    # State: (current_weight, items_selected_tuple, total_value)
    # Use tuple for items to make it hashable
    best_state = (0, (), 0)  # (weight, items, value)
    
    # BFS/DFS through state space
    queue = deque([(0, (), 0)])  # Start with empty knapsack
    visited = set()
    
    while queue:
        current_weight, current_items, current_value = queue.popleft()
        
        # Skip if we've seen this state (weight + items combination)
        state_key = (current_weight, current_items)
        if state_key in visited:
            continue
        visited.add(state_key)
        
        # Update best if this is better
        if current_value > best_state[2]:
            best_state = (current_weight, current_items, current_value)
        
        # Try adding each remaining item
        for item in items:
            if item['name'] in current_items:
                continue  # Item already selected
            
            new_weight = current_weight + item['weight']
            if new_weight <= capacity:
                new_items = current_items + (item['name'],)
                new_value = current_value + item['value']
                queue.append((new_weight, new_items, new_value))
    
    return best_state[2], list(best_state[1])

def main():
    # Read input
    with open('input.json', 'r') as f:
        data = json.load(f)
    
    items = data['items']
    capacity = data['capacity']
    
    print("=" * 60)
    print("Graph State-Space Traversal Solution (Option 2)")
    print("=" * 60)
    print(f"Capacity: {capacity}")
    print(f"Items: {len(items)}")
    print("\nItems:")
    for item in items:
        print(f"  {item['name']}: weight={item['weight']}, value={item['value']}")
    print()
    
    # Solve and time
    start_time = time.perf_counter()
    max_value, selected_items = knapsack_graph_statespace(items, capacity)
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

