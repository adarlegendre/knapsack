"""
Knapsack Problem - DP Bottom-Up Solution
Uses Option 2: State-space graph representation
Nodes = states (current_weight, items_selected)
Edge weights = value gained by adding an item
"""

import json
import time
from typing import List, Dict, Tuple

def knapsack_dp_bottomup(items: List[Dict], capacity: int) -> Tuple[int, List[str]]:
    """
    Solve 0/1 knapsack using bottom-up dynamic programming.
    Optimized: Pre-extract item properties, efficient inner loops.
    
    Args:
        items: List of items with 'name', 'weight', 'value'
        capacity: Maximum weight capacity
        
    Returns:
        Tuple of (max_value, selected_items)
    """
    n = len(items)
    
    # Pre-extract item properties to avoid dictionary lookups in inner loop
    item_weights = [item['weight'] for item in items]
    item_values = [item['value'] for item in items]
    item_names = [item['name'] for item in items]
    
    # dp[i][w] = maximum value using first i items with weight w
    # Use list of lists for efficient access
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    
    # Build DP table
    for i in range(1, n + 1):
        weight = item_weights[i - 1]
        value = item_values[i - 1]
        prev_row = dp[i - 1]
        curr_row = dp[i]
        
        # Copy previous row (don't take item)
        curr_row[:] = prev_row
        
        # Try taking item i (only for weights >= item weight)
        for w in range(weight, capacity + 1):
            candidate = prev_row[w - weight] + value
            if candidate > curr_row[w]:
                curr_row[w] = candidate
    
    # Backtrack to find selected items
    selected_items = []
    w = capacity
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            selected_items.append(item_names[i - 1])
            w -= item_weights[i - 1]
    
    selected_items.reverse()
    return dp[n][capacity], selected_items

def main():
    # Read input
    with open('input.json', 'r') as f:
        data = json.load(f)
    
    items = data['items']
    capacity = data['capacity']
    
    print("=" * 60)
    print("DP Bottom-Up Solution (State-Space Graph - Option 2)")
    print("=" * 60)
    print(f"Capacity: {capacity}")
    print(f"Items: {len(items)}")
    print("\nItems:")
    for item in items:
        print(f"  {item['name']}: weight={item['weight']}, value={item['value']}")
    print()
    
    # Solve and time
    start_time = time.perf_counter()
    max_value, selected_items = knapsack_dp_bottomup(items, capacity)
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

