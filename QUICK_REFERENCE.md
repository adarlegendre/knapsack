# Quick Reference Guide

## Running Benchmarks

### Small Scale (500-10K nodes)
```bash
# 1. Generate test cases
python test_generator.py 500 1000 2000 5000 10000

# 2. Run benchmarks
python benchmark.py

# 3. Visualize results
python visualize_results.py
```

### Large Scale (50K-200K+ nodes)
```bash
# All-in-one command (generates, benchmarks, visualizes)
python run_overnight.py 500 1000 5000 10000 50000 100000 200000
```

## File Structure

```
knapsack/
├── solution_*.py          # Solution implementations
├── graph_counter.py       # Count nodes/edges utility
├── test_generator.py      # Generate test cases
├── benchmark.py           # Run benchmarks (with timeout)
├── run_overnight.py       # Optimized overnight script (no timeout)
├── visualize_results.py   # Generate performance graphs
├── results/               # Test cases and results
│   ├── test_*.json        # Test case files
│   └── *.csv              # Benchmark results
├── graphs/                # Generated performance graphs
└── *.md                   # Documentation files
```

## Key Files

| File | Purpose |
|------|---------|
| `run_overnight.py` | **Main script** for large-scale benchmarking |
| `OPTIMIZATION_GUIDE.md` | **Detailed documentation** of all optimizations |
| `BENCHMARKING_GUIDE.md` | Benchmarking system documentation |
| `OVERNIGHT_GUIDE.md` | Overnight script usage guide |
| `WORKFLOW_GUIDE.md` | Complete workflow documentation |

## Common Commands

### Generate Test Cases
```bash
python test_generator.py 500 1000 2000 5000
```

### Benchmark Single Test Case
```bash
python benchmark.py
```

### Benchmark All (Overnight)
```bash
python run_overnight.py 500 1000 2000 5000 10000 50000 100000
```

### Visualize Results
```bash
python visualize_results.py results/overnight_benchmark_results.csv
```

### Check Progress (While Running)
```bash
# View log file
cat overnight_log.txt

# Or on Windows
type overnight_log.txt
```

## Performance Expectations

| Nodes | DP Solutions | Graph Solutions | Test Generation |
|-------|--------------|-----------------|-----------------|
| 1,000 | < 10 ms | ~100 ms | < 1 second |
| 10,000 | ~50 ms | ~5 seconds | ~30 seconds |
| 100,000 | ~500 ms | Skipped | ~15 minutes |
| 200,000 | ~1 second | Skipped | ~30 minutes |

## Troubleshooting

### Test Generation Fails
- **Solution**: Check `overnight_log.txt` for errors
- **Large targets**: May take 15-30 minutes, be patient
- **Tolerance**: Large targets allow 30% error

### Benchmarking Slow/Crashes
- **Solution**: Ensure graph solutions skipped for >= 5K nodes
- **Memory**: Check incremental CSV writing enabled
- **Progress**: Monitor `overnight_log.txt`

### Times Don't Match Console
- **Solution**: Regenerate graphs with `visualize_results.py`
- **Check**: CSV has both `*_time` and `*_actual_time` columns

## Documentation

- **`OPTIMIZATION_GUIDE.md`**: All optimizations explained
- **`BENCHMARKING_GUIDE.md`**: Benchmarking system details
- **`OVERNIGHT_GUIDE.md`**: Overnight script usage
- **`WORKFLOW_GUIDE.md`**: Complete workflow
- **`README.md`**: Project overview

## Tips

1. **Start Small**: Test with 500-5000 nodes first
2. **Use Overnight Script**: Handles everything automatically
3. **Monitor Progress**: Check `overnight_log.txt` regularly
4. **Resume Capability**: Script resumes from interruptions
5. **Graph Solutions**: Only for < 5K nodes (memory-intensive)



