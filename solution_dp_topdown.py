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
    Optimized: Pre-extract properties, efficient memoization, proper backtracking.
    
    Args:
        items: List of items with 'name', 'weight', 'value'
        capacity: Maximum weight capacity
        
    Returns:
        Tuple of (max_value, selected_items)
    """
    n = len(items)
    
    # Pre-extract item properties to avoid dictionary lookups
    item_weights = [item['weight'] for item in items]
    item_values = [item['value'] for item in items]
    item_names = [item['name'] for item in items]
    
    memo = {}  # (i, w) -> max_value
    
    def solve(i: int, w: int) -> int:
        """Recursive function with memoization (returns only value)."""
        if i == 0 or w == 0:
            return 0
        
        key = (i, w)
        if key in memo:
            return memo[key]
        
        weight = item_weights[i - 1]
        value = item_values[i - 1]
        
        # Don't take item i
        max_val = solve(i - 1, w)
        
        # Try taking item i
        if weight <= w:
            val_with_item = solve(i - 1, w - weight) + value
            if val_with_item > max_val:
                max_val = val_with_item
        
        memo[key] = max_val
        return max_val
    
    # Get max value
    max_value = solve(n, capacity)
    
    # Backtrack to find selected items using memo
    selected_items = []
    w = capacity
    
    for i in range(n, 0, -1):
        # Check if item i was taken by comparing memo values
        val_without = memo.get((i - 1, w), 0) if (i > 0) else 0
        val_with = memo.get((i, w), 0)
        
        if val_with != val_without:
            # Item i was taken
            selected_items.append(item_names[i - 1])
            w -= item_weights[i - 1]
    
    selected_items.reverse()
    return max_value, selected_items

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

