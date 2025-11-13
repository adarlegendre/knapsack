# Knapsack Problem - Graph Algorithm Solutions

This project implements multiple solutions to the 0/1 Knapsack Problem using different algorithmic approaches, all based on a state-space graph representation.

## Problem Description

The 0/1 Knapsack Problem: Given `n` items with weights and values, and a knapsack with capacity `W`, select a subset of items to maximize total value without exceeding the weight capacity. Each item can be taken at most once (0/1).

## Graph Representation: Option 2

We use **Option 2: State-Space Graph with Edge Weights as Values**.

### Our Choice: Option 2

**Nodes** = States `(current_weight, items_selected)`
- Each node represents a partial solution
- Example: `(5, ('A', 'B'))` means we've selected items A and B, with total weight 5

**Edges** = Transitions (adding one item)
- Directed edges from state to state
- Example: `(0, ()) → (5, ('A'))` represents adding item A

**Edge Weights** = Value gained by adding the item
- The weight of an edge equals the value of the item being added
- Example: If item A has value 10, the edge has weight 10

### Why Option 2?

#### ✅ Advantages:
1. **Natural DP Mapping**: Directly corresponds to dynamic programming transitions
2. **Clear State Progression**: Easy to visualize how solutions are built incrementally
3. **Efficient Representation**: States are naturally ordered (by weight/items), enabling optimization
4. **Multiple Algorithm Support**: Works well with DP, graph traversal, and DAG algorithms
5. **Intuitive**: Edge weights represent the "gain" from making a decision

#### ❌ Why Not Other Options?

**Option 1: Items as Nodes (Node Attributes)**
- ❌ Doesn't capture the state progression of building a solution
- ❌ Harder to model the constraint satisfaction (capacity limit)
- ❌ Would need complex edge structures for dependencies
- ✅ Good for: Item dependency graphs (if item A requires item B)

**Option 3: Edge Weights as Costs**
- ❌ Requires separate tracking of values vs weights
- ❌ Less intuitive (minimizing cost vs maximizing value)
- ✅ Good for: Network flow problems

**Option 4: Bipartite Graph**
- ❌ More complex structure
- ❌ Over-engineered for standard knapsack
- ✅ Good for: Assignment problems

## Solutions Implemented

### 1. `solution_dp_bottomup.py`
- **Approach**: Dynamic Programming (Bottom-Up)
- **Method**: Builds DP table iteratively
- **Time Complexity**: O(n × W)
- **Space Complexity**: O(n × W)
- **Best for**: Standard implementation, easy to understand

### 2. `solution_dp_topdown.py`
- **Approach**: Dynamic Programming (Top-Down with Memoization)
- **Method**: Recursive with memoization
- **Time Complexity**: O(n × W)
- **Space Complexity**: O(n × W)
- **Best for**: When you want recursive structure but DP efficiency

### 3. `solution_graph_statespace.py`
- **Approach**: Explicit State-Space Graph Traversal
- **Method**: BFS through all possible states
- **Time Complexity**: O(2^n) worst case, but pruned by capacity
- **Space Complexity**: O(2^n) worst case
- **Best for**: Understanding the graph structure explicitly

### 4. `solution_graph_dag.py`
- **Approach**: DAG Longest Path
- **Method**: Models states as DAG nodes, finds longest path
- **Time Complexity**: O(V + E) where V = states, E = transitions
- **Space Complexity**: O(V + E)
- **Best for**: Graph algorithm perspective, topological sort application

## Input Format

The input file `input.json` contains:

```json
{
  "capacity": 10,
  "items": [
    {"name": "A", "weight": 5, "value": 10},
    {"name": "B", "weight": 3, "value": 7},
    ...
  ]
}
```

## Usage

Run any solution file:

```bash
python solution_dp_bottomup.py
python solution_dp_topdown.py
python solution_graph_statespace.py
python solution_graph_dag.py
```

## Output Format

Each solution prints:
- Problem details (capacity, items)
- **Selected items**: List of item names in optimal solution
- **Total value**: Maximum value achieved
- **Execution time**: Time taken in milliseconds

Example output:
```
============================================================
DP Bottom-Up Solution (State-Space Graph - Option 2)
============================================================
Capacity: 10
Items: 5

Items:
  A: weight=5, value=10
  B: weight=3, value=7
  ...

Results:
  Selected items: ['B', 'C', 'D']
  Total value: 20
  Execution time: 0.1234 ms
============================================================
```

## Performance Analysis

All solutions include execution time measurement for performance comparison. You can:
1. Modify `input.json` with different problem sizes
2. Run all solutions and compare execution times
3. Generate performance graphs for different graph sizes

## Benchmarking and Performance Testing

The project includes a comprehensive benchmarking system to test solutions across different graph sizes and compare their performance.

### Benchmarking Tools

#### 1. `graph_counter.py` - Graph Metrics Utility
Counts the number of nodes (states) and edges (transitions) in the state-space graph for a given input.

**Usage:**
```bash
python graph_counter.py [input_file]
```

**Example:**
```bash
python graph_counter.py input.json
```

**Output:**
```
Graph Metrics for input.json:
  Nodes (states): 32
  Edges (transitions): 87
  Number of items: 5
  Capacity: 10
  Average weight: 4.00
  Average value: 8.40
```

#### 2. `test_generator.py` - Test Case Generator
Generates knapsack problem instances that target specific graph sizes (nodes and edges).

**Usage:**
```bash
# Generate default test cases (500, 1000, 1500, ... up to 100000 nodes)
python test_generator.py

# Generate custom test cases
python test_generator.py 500 1500 2000 2500 10000
```

**Features:**
- Iterative refinement to find parameters that produce graphs close to target sizes
- Accepts ±10% tolerance from target
- Saves test cases to `results/` directory
- Includes metadata about actual vs target graph sizes

**Output:**
- Test case files: `results/test_500.json`, `results/test_1000.json`, etc.
- Each file contains items, capacity, and metadata

#### 3. `benchmark.py` - Performance Benchmarking
Runs all solutions on test cases and collects performance metrics.

**Usage:**
```bash
# Benchmark all test cases in results/ directory
python benchmark.py

# Specify custom directories
python benchmark.py [test_dir] [output_csv]
```

**Features:**
- Runs all 4 solutions on each test case
- Measures execution time (milliseconds)
- Handles timeouts (5 minutes default) and errors gracefully
- Exports results to CSV for analysis
- Shows summary table of results

**Output:**
- CSV file: `results/benchmark_results.csv` with columns:
  - `test_file`, `target_nodes`, `actual_nodes`, `actual_edges`
  - `num_items`, `capacity`
  - `dp_bottomup_time`, `dp_bottomup_status`
  - `dp_topdown_time`, `dp_topdown_status`
  - `graph_statespace_time`, `graph_statespace_status`
  - `graph_dag_time`, `graph_dag_status`

#### 4. `visualize_results.py` - Performance Visualization
Generates performance graphs from benchmark results.

**Usage:**
```bash
# Generate all graphs from default CSV
python visualize_results.py

# Specify custom CSV file
python visualize_results.py results/benchmark_results.csv
```

**Output Graphs:**
- `graphs/runtime_vs_nodes.png` - Runtime vs number of nodes (log scale)
- `graphs/runtime_vs_edges.png` - Runtime vs number of edges (log scale)
- `graphs/scalability_comparison.png` - Side-by-side comparison

**Features:**
- Log-log scale for wide data ranges
- Multiple solution comparison
- High-resolution output (300 DPI)
- Automatic handling of failed/timeout solutions

### Complete Benchmarking Workflow

1. **Generate Test Cases:**
   ```bash
   python test_generator.py 500 1500 2000 2500 5000 10000
   ```

2. **Run Benchmarks:**
   ```bash
   python benchmark.py
   ```

3. **Visualize Results:**
   ```bash
   python visualize_results.py
   ```

### Expected Performance Characteristics

Based on algorithm complexity:

- **DP Solutions (Bottom-Up & Top-Down)**:
  - Time: O(n × W) where n = items, W = capacity
  - Should scale well to large inputs (10,000+ nodes)
  - Memory: O(n × W)

- **Graph State-Space**:
  - Time: O(2^n) worst case, pruned by capacity
  - May timeout on large inputs (>5,000 nodes)
  - Memory: O(2^n) worst case

- **Graph DAG**:
  - Time: O(V + E) where V = nodes, E = edges
  - May timeout on large inputs (>10,000 nodes)
  - Memory: O(V + E)

### Benchmarking Tips

1. **Start Small**: Test with small sizes first (500-5000 nodes) to validate setup
2. **Progressive Testing**: Increase sizes gradually to find breaking points
3. **Timeout Handling**: Graph solutions may timeout on large inputs - this is expected
4. **Results Analysis**: Check CSV file for detailed metrics and status codes
5. **Graph Interpretation**: Use log scale graphs to see exponential vs polynomial behavior

### File Structure

```
knapsack/
├── solution_*.py          # Solution implementations
├── graph_counter.py       # Count nodes/edges utility
├── test_generator.py      # Generate test cases
├── benchmark.py           # Run benchmarks
├── visualize_results.py   # Generate graphs
├── results/               # Test cases and results
│   ├── test_500.json
│   ├── test_1000.json
│   └── benchmark_results.csv
└── graphs/                # Generated performance graphs
    ├── runtime_vs_nodes.png
    ├── runtime_vs_edges.png
    └── scalability_comparison.png
```

### Dependencies

For visualization, install matplotlib:
```bash
pip install matplotlib
```

## Future Work

- Memory usage tracking in benchmarks
- Interactive visualization (plotly)
- Additional solution approaches (branch-and-bound, genetic algorithms)
- Graph visualization of state-space structure

