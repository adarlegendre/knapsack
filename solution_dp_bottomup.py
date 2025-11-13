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
    
    Args:
        items: List of items with 'name', 'weight', 'value'
        capacity: Maximum weight capacity
        
    Returns:
        Tuple of (max_value, selected_items)
    """
    n = len(items)
    # dp[i][w] = maximum value using first i items with weight w
    dp = [[0 for _ in range(capacity + 1)] for _ in range(n + 1)]
    # Track which items were selected
    selected = [[[] for _ in range(capacity + 1)] for _ in range(n + 1)]
    
    # Build DP table
    for i in range(1, n + 1):
        item = items[i - 1]
        weight = item['weight']
        value = item['value']
        name = item['name']
        
        for w in range(capacity + 1):
            # Don't take item i
            dp[i][w] = dp[i - 1][w]
            selected[i][w] = selected[i - 1][w].copy()
            
            # Try taking item i
            if weight <= w:
                if dp[i - 1][w - weight] + value > dp[i][w]:
                    dp[i][w] = dp[i - 1][w - weight] + value
                    selected[i][w] = selected[i - 1][w - weight] + [name]
    
    return dp[n][capacity], selected[n][capacity]

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

