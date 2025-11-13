# Benchmarking Guide

Quick start guide for benchmarking knapsack solutions across different graph sizes.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate Test Cases
Generate test cases for specific graph sizes (nodes):
```bash
python test_generator.py 500 1500 2000 2500 5000 10000
```

Or use default sizes (500 to 100,000):
```bash
python test_generator.py
```

### 3. Run Benchmarks
Run all solutions on generated test cases:
```bash
python benchmark.py
```

This will:
- Run all 4 solutions on each test case
- Measure execution time
- Handle timeouts and errors
- Save results to `results/benchmark_results.csv`

### 4. Visualize Results
Generate performance graphs:
```bash
python visualize_results.py
```

This creates:
- `graphs/runtime_vs_nodes.png`
- `graphs/runtime_vs_edges.png`
- `graphs/scalability_comparison.png`

## Understanding Results

### CSV Output Columns

- `test_file`: Path to test case file
- `target_nodes`: Target number of nodes
- `actual_nodes`: Actual number of nodes in graph
- `actual_edges`: Actual number of edges in graph
- `num_items`: Number of items in problem
- `capacity`: Knapsack capacity
- `*_time`: Execution time in milliseconds (or None if failed)
- `*_status`: Status (SUCCESS, TIMEOUT, or ERROR message)

### Status Codes

- `SUCCESS`: Solution completed successfully
- `TIMEOUT`: Solution exceeded 5-minute timeout
- `ERROR: ...`: Solution encountered an error

### Expected Behavior

- **DP Solutions**: Should work on all sizes (up to 100,000+ nodes)
- **Graph Solutions**: May timeout on large sizes (>5,000-10,000 nodes)
  - This is expected due to exponential complexity
  - Timeouts are handled gracefully

## Customization

### Change Timeout
Edit `benchmark.py`:
```python
TIMEOUT_SECONDS = 600  # 10 minutes
```

### Custom Test Sizes
```bash
python test_generator.py 100 500 1000 2000 5000
```

### Custom Output Location
```bash
python benchmark.py results custom_output.csv
python visualize_results.py custom_output.csv
```

## Troubleshooting

### "No test files found"
- Run `test_generator.py` first to create test cases

### "Module not found"
- Install dependencies: `pip install -r requirements.txt`

### Graph solutions timeout
- This is expected for large inputs
- Try smaller test sizes first
- DP solutions should still work

### Test generation takes long
- Large target sizes (>50,000) may take time
- The generator tries multiple parameter combinations
- Be patient or reduce target sizes

## Performance Tips

1. **Start Small**: Test with 500-5000 nodes first
2. **Progressive Testing**: Increase sizes gradually
3. **Check CSV**: Detailed metrics in CSV file
4. **Log Scale**: Graphs use log scale for wide ranges
5. **Compare Solutions**: See which scales better

## Example Workflow

```bash
# 1. Generate small test cases
python test_generator.py 500 1000 2000 5000

# 2. Run benchmarks
python benchmark.py

# 3. Check results
cat results/benchmark_results.csv

# 4. Generate graphs
python visualize_results.py

# 5. View graphs
# Open graphs/runtime_vs_nodes.png
```

## Next Steps

- Analyze CSV data for detailed insights
- Compare different solution approaches
- Identify scalability limits
- Optimize solutions based on findings

