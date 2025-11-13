"""
Knapsack Problem - DP Top-Down (Memoized) Solution
Uses Option 2: State-space graph representation
Nodes = states (current_weight, items_selected)
Edge weights = value gained by adding an item
"""

import json
import time
from typing import List, Dict, Tuple, Optional

def knapsack_dp_topdown(items: List[Dict], capacity: int) -> Tuple[int, List[str]]:
    """
    Solve 0/1 knapsack using top-down dynamic programming with memoization.
    
    Args:
        items: List of items with 'name', 'weight', 'value'
        capacity: Maximum weight capacity
        
    Returns:
        Tuple of (max_value, selected_items)
    """
    n = len(items)
    memo = {}  # (i, w) -> (max_value, selected_items)
    
    def solve(i: int, w: int) -> Tuple[int, List[str]]:
        """Recursive function with memoization."""
        if i == 0 or w == 0:
            return 0, []
        
        if (i, w) in memo:
            return memo[(i, w)]
        
        item = items[i - 1]
        weight = item['weight']
        value = item['value']
        name = item['name']
        
        # Don't take item i
        max_val, selected = solve(i - 1, w)
        
        # Try taking item i
        if weight <= w:
            val_with_item, items_with = solve(i - 1, w - weight)
            if val_with_item + value > max_val:
                max_val = val_with_item + value
                selected = items_with + [name]
        
        memo[(i, w)] = (max_val, selected)
        return max_val, selected
    
    return solve(n, capacity)

def main():
    # Read input
    with open('input.json', 'r') as f:
        data = json.load(f)
    
    items = data['items']
    capacity = data['capacity']
    
    print("=" * 60)
    print("DP Top-Down (Memoized) Solution (State-Space Graph - Option 2)")
    print("=" * 60)
    print(f"Capacity: {capacity}")
    print(f"Items: {len(items)}")
    print("\nItems:")
    for item in items:
        print(f"  {item['name']}: weight={item['weight']}, value={item['value']}")
    print()
    
    # Solve and time
    start_time = time.perf_counter()
    max_value, selected_items = knapsack_dp_topdown(items, capacity)
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

