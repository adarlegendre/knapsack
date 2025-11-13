# Overnight Benchmarking Guide

## Overview

The `run_overnight.py` script is designed to run unattended overnight without timeout restrictions. It will:
1. Generate test cases for specified graph sizes
2. Run all solutions with NO TIMEOUT limits
3. Save all results to CSV
4. Log everything to `overnight_log.txt`

## Usage

### Basic Usage (Default Sizes)
```bash
python run_overnight.py
```
Runs with default sizes: 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000

### Custom Sizes
```bash
python run_overnight.py 500 1000 5000 10000 50000 100000
```

### Large Scale (1 Million Nodes)
```bash
python run_overnight.py 1000000
```
⚠️ **Warning**: This may take many hours or days!

## Features

### ✅ No Timeout Restrictions
- Solutions run until completion
- No 5-minute limit
- Perfect for large test cases

### ✅ Automatic Test Generation
- Generates test cases if they don't exist
- Skips existing test cases
- Uses more attempts for large sizes

### ✅ Comprehensive Logging
- All output logged to `overnight_log.txt`
- Timestamps on every message
- Progress tracking

### ✅ Error Handling
- Continues if one test case fails
- Saves partial results
- Safe to interrupt (Ctrl+C)

### ✅ Results Saved
- CSV file: `results/overnight_benchmark_results.csv`
- All execution times recorded
- Actual times even on errors

## Output Files

### 1. `overnight_log.txt`
Complete log of the entire run:
```
[2025-11-12 20:00:00] Overnight Benchmarking - NO TIMEOUT RESTRICTIONS
[2025-11-12 20:00:01] Target sizes: [500, 1000, 5000]
[2025-11-12 20:00:02] STEP 1: Generating test cases...
[2025-11-12 20:05:30]   [OK] Generated: results/test_500.json
...
```

### 2. `results/overnight_benchmark_results.csv`
CSV file with all benchmark results:
- All test cases
- All solutions
- Execution times
- Status codes
- Actual times (even on timeout/error)

## Running Overnight

### Step 1: Prepare
```bash
# Make sure you have dependencies
pip install -r requirements.txt

# Check you have enough disk space
# Large test cases can generate large files
```

### Step 2: Start the Script
```bash
# For default sizes
python run_overnight.py

# Or custom sizes
python run_overnight.py 500 1000 5000 10000 50000 100000
```

### Step 3: Leave It Running
- Script will run until all test cases are processed
- Can safely leave computer overnight
- Check `overnight_log.txt` for progress

### Step 4: Check Results in Morning
```bash
# View log
cat overnight_log.txt

# View results
cat results/overnight_benchmark_results.csv
```

## Expected Runtime

| Graph Size | Test Generation | Benchmarking (DP) | Benchmarking (Graph) |
|------------|----------------|-------------------|----------------------|
| 500-2000   | 1-5 minutes    | < 1 second       | 1-10 seconds        |
| 5000-10000 | 5-15 minutes   | 1-5 seconds      | 1-5 minutes         |
| 20000-50000| 15-60 minutes  | 5-30 seconds     | 10-60 minutes       |
| 100000     | 1-3 hours      | 1-5 minutes       | 1-3 hours           |
| 1000000    | 3-12 hours     | 5-30 minutes      | 6-24 hours          |

**Total for all sizes**: 4-12 hours (depending on sizes)

## Tips

### 1. Start Small
Test with small sizes first:
```bash
python run_overnight.py 500 1000 2000
```

### 2. Monitor Progress
Check log file periodically:
```bash
tail -f overnight_log.txt
```

### 3. Interrupt Safely
Press Ctrl+C to stop - partial results are saved

### 4. Resume Later
- Script skips existing test cases
- Can re-run to complete missing benchmarks
- Results are appended/updated

### 5. Large Sizes
For 100K+ nodes:
- Ensure sufficient RAM (8GB+ recommended)
- May take many hours
- Consider running only DP solutions (modify script)

## Troubleshooting

### Script Stops Unexpectedly
- Check `overnight_log.txt` for errors
- May be out of memory for very large sizes
- Try smaller sizes first

### Test Generation Takes Too Long
- Large sizes (100K+) can take hours
- This is normal - be patient
- Consider reducing target sizes

### Out of Memory
- Close other applications
- Reduce target sizes
- Consider testing only DP solutions

### Results Not Saved
- Check if script was interrupted
- Check disk space
- Verify write permissions

## Example Output

```
================================================================================
Overnight Benchmarking - NO TIMEOUT RESTRICTIONS
================================================================================
Target sizes: [500, 1000, 5000, 10000]

STEP 1: Generating test cases...
  Test case 500 already exists: results/test_500.json
  Generating test case for 1000 nodes...
    [OK] Generated: results/test_1000.json
    Actual: 1109 nodes, 4500 edges

STEP 2: Benchmarking all test cases (NO TIMEOUT)...
[1/4] test_500.json
  Running dp_bottomup...
    [OK] 1.05 ms (0.00 min)
  Running graph_statespace...
    [OK] 625.03 ms (0.01 min)

Summary:
     Nodes   DP-BU (ms)   Graph-SS (ms)
       369         1.05          625.03
      1109         1.20         2119.31
```

## Next Steps

After overnight run:
1. Check `overnight_log.txt` for any errors
2. View `results/overnight_benchmark_results.csv`
3. Generate visualizations:
   ```bash
   python visualize_results.py results/overnight_benchmark_results.csv
   ```
4. Analyze performance trends

