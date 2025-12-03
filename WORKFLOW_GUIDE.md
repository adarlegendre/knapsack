# Complete Workflow Guide: Generate Test Cases → Benchmark → Visualize

## Overview

This guide explains how to:
1. Generate test cases for sizes 100-100K
2. Run benchmarks on all test cases
3. Generate performance graphs

## Two-Phase Approach

### Phase 1: Generate Test Cases (One-Time)

Generate all test cases first. This can take many hours, but you only do it once.

```bash
# Generate test cases for all sizes
python run_overnight.py 100 200 300 500 1000 1500 2000 2500 5000 10000 30000 50000 100000
```

**What happens:**
- Generates test case files: `test_100.json`, `test_200.json`, etc.
- Skips existing test cases (safe to re-run)
- Takes 12-24+ hours for large sizes
- Can be interrupted and resumed

**Output:**
- Test case files in `results/` directory
- Each file contains items, capacity, and metadata

### Phase 2: Run Benchmarks (After Test Cases Ready)

Once all test cases are generated, run benchmarks:

```bash
# Benchmark all test cases
python run_overnight.py 100 200 300 500 1000 1500 2000 2500 5000 10000 30000 50000 100000
```

**What happens:**
- Skips test case generation (files already exist)
- Runs benchmarks on all test cases
- **Graph solutions skipped for sizes >= 10,000 nodes** (memory optimization)
- Saves results incrementally to CSV
- Generates performance graphs automatically

**Output:**
- `results/overnight_benchmark_results.csv` - All benchmark data
- `graphs/runtime_vs_nodes.png` - Performance graph
- `graphs/runtime_vs_edges.png` - Performance graph
- `graphs/scalability_comparison.png` - Comparison graph

## Graph Solution Skipping Logic

**Automatic behavior:**
- Sizes < 10,000: All 4 solutions run (DP Bottom-Up, DP Top-Down, Graph State-Space, Graph DAG)
- Sizes >= 10,000: Only DP solutions run (Graph solutions skipped)

**Why:**
- Graph solutions use exponential memory (2^n states)
- For 10K+ nodes, they would take hours and use 10GB+ RAM
- DP solutions scale well and complete in seconds/minutes

**What you get:**
- Complete comparison for small/medium sizes (all 4 solutions)
- DP scalability data for all sizes (shows polynomial scaling)
- Graph scalability data for small/medium sizes (shows exponential behavior)

## Example Workflow

### Day 1: Generate Test Cases

```bash
# Start test case generation (can run overnight)
python run_overnight.py 100 200 300 500 1000 1500 2000 2500 5000 10000 30000 50000 100000

# Check progress
tail -f overnight_log.txt

# If interrupted, just re-run - it will skip existing test cases
```

**Time:** 12-24+ hours (mostly waiting for large sizes)

### Day 2: Run Benchmarks

```bash
# Once all test cases are generated, run benchmarks
python run_overnight.py 100 200 300 500 1000 1500 2000 2500 5000 10000 30000 50000 100000

# This will:
# - Skip test case generation (files exist)
# - Run benchmarks on all test cases
# - Skip graph solutions for 10K+
# - Generate graphs automatically
```

**Time:** 10-30 minutes (DP solutions are fast)

## What the Graphs Will Show

### For Sizes < 10,000:
- **4 lines**: DP Bottom-Up, DP Top-Down, Graph State-Space, Graph DAG
- Shows exponential vs polynomial scaling
- Complete comparison

### For Sizes >= 10,000:
- **2 lines**: DP Bottom-Up, DP Top-Down
- Shows polynomial scaling continues
- Graph solutions not shown (would be off the chart anyway)

## Resume Capability

**Test Case Generation:**
- If interrupted, re-run the same command
- Skips existing test cases
- Continues from where it stopped

**Benchmarking:**
- If interrupted, re-run the same command
- Skips completed benchmarks
- Continues from where it stopped
- Results saved incrementally

## Expected Results

### Test Case Generation Times:
- 100-500: Seconds to minutes
- 1000-5000: Minutes to hours
- 10000: 1-2 hours
- 30000: 2-4 hours
- 50000: 3-6 hours
- 100000: 6-12+ hours

### Benchmark Times:
- Sizes < 10K: ~1-10 minutes total (all solutions)
- Sizes >= 10K: ~5-15 minutes total (DP only)

## Tips

1. **Generate test cases first**: Let it run overnight
2. **Check log file**: Monitor progress with `tail -f overnight_log.txt`
3. **Resume is automatic**: Re-run same command to continue
4. **Graphs generated automatically**: After benchmarks complete
5. **Memory optimized**: Graph solutions skipped for large sizes

## Summary

✅ **Generate test cases once** (12-24+ hours)
✅ **Run benchmarks later** (10-30 minutes)
✅ **Graphs generated automatically**
✅ **All sizes 100-100K supported**
✅ **Graph solutions skipped for 10K+** (memory efficient)

You'll get comprehensive performance data across all sizes!


