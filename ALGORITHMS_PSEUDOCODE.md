# Knapsack Algorithms - Pseudocode with Runtime Analysis

## Algorithm 1: DP Bottom-Up (Iterative Dynamic Programming)

```
KNAPSACK-DP-BOTTOMUP(items, capacity)
1  n ← length(items)                          // O(1)
2  W ← capacity                               // O(1)
3  
4  // Pre-extract item properties             // O(n) total
5  weights[1..n] ← extract weights from items  // O(n)
6  values[1..n] ← extract values from items    // O(n)
7  names[1..n] ← extract names from items     // O(n)
8  
9  // Initialize DP table                      // O(n*W) space
10 dp[0..n][0..W] ← 0                          // O(n*W)
11 
12 // Build DP table                          // O(n*W) time
13 for i ← 1 to n                              // O(n) iterations
14     do weight ← weights[i]                  // O(1)
15        value ← values[i]                    // O(1)
16        // Copy previous row (don't take item)
17        dp[i] ← dp[i-1]                      // O(W) - row copy
18        // Try taking item i
19        for w ← weight to W                  // O(W) iterations per item
20            do candidate ← dp[i-1][w-weight] + value  // O(1)
21               if candidate > dp[i][w]       // O(1)
22                  then dp[i][w] ← candidate  // O(1)
23 
24 // Backtrack to find selected items         // O(n) time
25 selected ← empty list                       // O(1)
26 w ← W                                       // O(1)
27 for i ← n downto 1                         // O(n) iterations
28     do if dp[i][w] ≠ dp[i-1][w]            // O(1)
29           then selected.append(names[i])    // O(1)
30                w ← w - weights[i]           // O(1)
31 
32 reverse(selected)                           // O(n)
33 return (dp[n][W], selected)                 // O(1)

Total Runtime: O(n*W) where n = number of items, W = capacity
Space: O(n*W) for DP table
```

---

## Algorithm 2: DP Top-Down (Memoized Recursive Dynamic Programming)

```
KNAPSACK-DP-TOPDOWN(items, capacity)
1  n ← length(items)                          // O(1)
2  W ← capacity                               // O(1)
3  
4  // Pre-extract item properties             // O(n) total
5  weights[1..n] ← extract weights from items  // O(n)
6  values[1..n] ← extract values from items    // O(n)
7  names[1..n] ← extract names from items     // O(n)
8  
9  memo ← empty dictionary                    // O(1)
10 
11 // Recursive function with memoization
12 function SOLVE(i, w)                        // Called O(n*W) times worst case
13     if i = 0 or w = 0                       // O(1)
14        then return 0                        // O(1)
15     
16     key ← (i, w)                            // O(1)
17     if key ∈ memo                           // O(1) hash lookup
18        then return memo[key]                // O(1)
19     
20     weight ← weights[i]                     // O(1)
21     value ← values[i]                        // O(1)
22     
23     // Don't take item i
24     max_val ← SOLVE(i-1, w)                 // O(1) recursive call (memoized)
25     
26     // Try taking item i
27     if weight ≤ w                            // O(1)
28        then val_with_item ← SOLVE(i-1, w-weight) + value  // O(1) recursive call
29             if val_with_item > max_val       // O(1)
30                then max_val ← val_with_item  // O(1)
31     
32     memo[key] ← max_val                      // O(1) hash insert
33     return max_val                           // O(1)
34 
35 // Get max value
36 max_value ← SOLVE(n, W)                     // O(n*W) time
37 
38 // Backtrack to find selected items         // O(n) time
39 selected ← empty list                       // O(1)
40 w ← W                                       // O(1)
41 for i ← n downto 1                         // O(n) iterations
42     do val_without ← memo[(i-1, w)]         // O(1) hash lookup
43        val_with ← memo[(i, w)]              // O(1) hash lookup
44        if val_with ≠ val_without            // O(1)
45           then selected.append(names[i])    // O(1)
46                w ← w - weights[i]            // O(1)
47 
48 reverse(selected)                           // O(n)
49 return (max_value, selected)                 // O(1)

Total Runtime: O(n*W) worst case, but typically better due to memoization
Space: O(n*W) for memoization dictionary + O(n) recursion stack
```

---

## Algorithm 3: Graph State-Space Traversal (BFS)

```
KNAPSACK-GRAPH-STATESPACE(items, capacity)
1  n ← length(items)                          // O(1)
2  W ← capacity                               // O(1)
3  
4  best_state ← (0, ∅, 0)                     // O(1) - (weight, items, value)
5  queue ← empty queue                        // O(1)
6  ENQUEUE(queue, (0, ∅, 0))                 // O(1) - start state
7  visited ← empty set                        // O(1)
8  
9  while queue ≠ ∅                            // O(2^n) worst case - all states
10    do (current_weight, current_items, current_value) ← DEQUEUE(queue)  // O(1)
11       
12       state_key ← (current_weight, current_items)  // O(n) - tuple creation
13       if state_key ∈ visited                // O(1) hash lookup
14          then continue                      // O(1)
15       visited.add(state_key)                // O(1) hash insert
16       
17       // Update best if this is better
18       if current_value > best_state.value   // O(1)
19          then best_state ← (current_weight, current_items, current_value)  // O(n)
20       
21       // Try adding each remaining item     // O(n) per state
22       for each item ∈ items                 // O(n) iterations
23          do if item.name ∈ current_items    // O(n) - set membership check
24                then continue                // O(1)
25             
26             new_weight ← current_weight + item.weight  // O(1)
27             if new_weight ≤ capacity        // O(1)
28                then new_items ← current_items ∪ {item.name}  // O(n) - set union
29                     new_value ← current_value + item.value    // O(1)
30                     ENQUEUE(queue, (new_weight, new_items, new_value))  // O(1)
31 
32 return (best_state.value, best_state.items)  // O(1)

Total Runtime: O(2^n * n) worst case - explores all 2^n possible item combinations
Space: O(2^n) for visited set and queue
Note: In practice, many states are pruned due to capacity constraints, 
      but worst case remains exponential.
```

---

## Algorithm 4: Graph DAG Longest Path

```
KNAPSACK-GRAPH-DAG(items, capacity)
1  n ← length(items)                          // O(1)
2  W ← capacity                               // O(1)
3  
4  // Build DAG                               // O(V + E) where V = states, E = edges
5  graph ← empty adjacency list               // O(1)
6  in_degree ← empty dictionary               // O(1)
7  nodes ← empty set                          // O(1)
8  
9  start ← (0, ∅)                             // O(1)
10 nodes.add(start)                            // O(1)
11 queue ← empty queue                        // O(1)
12 ENQUEUE(queue, start)                      // O(1)
13 visited ← empty set                        // O(1)
14 
15 // Build graph by exploring all reachable states
16 while queue ≠ ∅                             // O(V) iterations - all states
17    do current_state ← DEQUEUE(queue)        // O(1)
18       if current_state ∈ visited           // O(1) hash lookup
19          then continue                     // O(1)
20       visited.add(current_state)           // O(1)
21       
22       (current_weight, current_items) ← current_state  // O(1)
23       
24       // Try adding each item not yet selected  // O(n) per state
25       for each item ∈ items                 // O(n) iterations
26          do if item.name ∈ current_items    // O(n) - set membership
27                then continue               // O(1)
28             
29             new_weight ← current_weight + item.weight  // O(1)
30             if new_weight ≤ capacity       // O(1)
31                then new_items ← sorted(current_items ∪ {item.name})  // O(n log n)
32                     new_state ← (new_weight, new_items)  // O(n)
33                     
34                     // Add edge with weight = item value
35                     graph[current_state].append((new_state, item.value))  // O(1)
36                     in_degree[new_state] ← in_degree[new_state] + 1  // O(1)
37                     
38                     if new_state ∉ visited   // O(1)
39                        then ENQUEUE(queue, new_state)  // O(1)
40                             nodes.add(new_state)  // O(1)
41 
42 // Longest path in DAG using DP             // O(V + E) time
43 dist ← empty dictionary                    // O(1)
44 for each node ∈ nodes                      // O(V) iterations
45    do dist[node] ← (0, ∅)                  // O(1)
46 
47 dist[start] ← (0, ∅)                       // O(1)
48 queue ← empty queue                        // O(1)
49 ENQUEUE(queue, start)                      // O(1)
50 processed ← empty set                      // O(1)
51 
52 // Process nodes in topological order (BFS)
53 while queue ≠ ∅                            // O(V) iterations
54    do u ← DEQUEUE(queue)                   // O(1)
55       if u ∈ processed                     // O(1)
56          then continue                     // O(1)
57       processed.add(u)                      // O(1)
58       
59       for each (v, edge_weight) ∈ graph[u]  // O(E) total across all iterations
60          do new_value ← dist[u].value + edge_weight  // O(1)
61             if new_value > dist[v].value    // O(1)
62                then dist[v] ← (new_value, items_from_state(v))  // O(n)
63             
64             in_degree[v] ← in_degree[v] - 1  // O(1)
65             if in_degree[v] = 0             // O(1)
66                then ENQUEUE(queue, v)       // O(1)
67 
68 // Find node with maximum value             // O(V) time
69 best_node ← argmax(dist, key=value)        // O(V)
70 return (dist[best_node].value, dist[best_node].items)  // O(1)

Total Runtime: O(V + E) where V = number of states (can be O(2^n)), E = number of edges
Space: O(V + E) for graph representation
Note: V and E can be exponential in worst case, making this O(2^n) in practice.
      The DAG structure allows topological sort, but state space is still exponential.
```

---

## Summary of Runtime Complexities

| Algorithm | Time Complexity | Space Complexity | Notes |
|-----------|----------------|------------------|-------|
| **DP Bottom-Up** | O(n·W) | O(n·W) | Polynomial in n and W. W can be large. |
| **DP Top-Down** | O(n·W) | O(n·W) | Same as bottom-up, but may compute fewer subproblems due to memoization. |
| **Graph State-Space** | O(2^n · n) | O(2^n) | Exponential - explores all possible item combinations. |
| **Graph DAG** | O(V + E) | O(V + E) | V = states (O(2^n) worst case), E = transitions. Exponential in worst case. |

Where:
- **n** = number of items
- **W** = knapsack capacity
- **V** = number of states in state-space graph (exponential in worst case)
- **E** = number of edges/transitions in state-space graph

---

## Key Observations

1. **DP solutions (Bottom-Up & Top-Down)** are polynomial in the input size (n, W) but pseudo-polynomial since W can be large.

2. **Graph solutions (State-Space & DAG)** are exponential in the number of items, as they explicitly explore the state space.

3. **DP Bottom-Up** is typically faster than Top-Down for small problems due to cache locality, but Top-Down may skip unnecessary subproblems.

4. **Graph DAG** has better theoretical structure (topological sort) but still suffers from exponential state space in practice.

5. For large problems (many items or large capacity), DP solutions are preferred. Graph solutions are only practical for very small instances.

