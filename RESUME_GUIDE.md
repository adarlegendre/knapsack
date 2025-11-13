# Resume Guide - Continuing from Interruption

## How Resume Works

The `run_overnight.py` script now supports **automatic resume**:

1. **Test Case Generation**: Already resumes - skips existing test files
2. **Benchmarking**: Now resumes - skips test cases with complete results
3. **Results**: Merges old and new results automatically

## How to Resume

### Simple: Just Re-run the Same Command

```bash
# If interrupted, just run again:
python run_overnight.py 1000000
```

The script will:
- ✅ Skip test case generation (if `test_1000000.json` exists)
- ✅ Skip completed benchmarks (if already in CSV)
- ✅ Only run missing/incomplete benchmarks
- ✅ Merge all results into CSV

### Example Scenario: 1 Million Nodes

**First Run (Interrupted):**
```bash
python run_overnight.py 1000000
# Runs for 3 hours, then computer crashes
```

**Resume (Next Day):**
```bash
python run_overnight.py 1000000
# Script detects:
# - test_1000000.json exists → SKIP generation
# - CSV has partial results → Only run missing benchmarks
# - Continues from where it left off
```

## What Gets Resumed

### ✅ Automatically Resumed:
- **Test case files** (`test_*.json`) - If exists, skipped
- **Complete benchmarks** - If all 4 solutions completed, skipped
- **Partial results** - Saved to CSV even if interrupted

### ⚠️ Re-run (Not Resumed):
- **Incomplete benchmarks** - If a solution failed/timeout, will re-run
- **Missing test cases** - Will generate if file doesn't exist

## Resume Detection

The script considers a test case "complete" if:
- ✅ DP Bottom-Up: SUCCESS
- ✅ DP Top-Down: SUCCESS  
- ✅ Graph State-Space: SUCCESS, TIMEOUT, or ERROR (any status)
- ✅ Graph DAG: SUCCESS, TIMEOUT, or ERROR (any status)

If all 4 solutions have a status (even if failed), it's considered complete and skipped.

## Manual Resume Options

### Option 1: Check What's Done
```bash
# View existing results
cat results/overnight_benchmark_results.csv

# Check log
tail overnight_log.txt
```

### Option 2: Resume Specific Test Case
If you only want to complete one test case:
```bash
# The script will automatically skip completed ones
python run_overnight.py 1000000
```

### Option 3: Force Re-run (Delete CSV)
If you want to start fresh:
```bash
# Backup existing results first!
cp results/overnight_benchmark_results.csv results/backup.csv

# Delete to force re-run
rm results/overnight_benchmark_results.csv

# Run again
python run_overnight.py 1000000
```

## Example Resume Output

```
STEP 2: Benchmarking all test cases (NO TIMEOUT)...
  Found existing results for: test_500.json
  Found existing results for: test_1000.json
  Found existing results for: test_5000.json
  Resuming: 3 test cases already completed

[1/5] test_500.json [SKIP - Already completed]
[2/5] test_1000.json [SKIP - Already completed]
[3/5] test_5000.json [SKIP - Already completed]
[4/5] test_10000.json
  Running dp_bottomup...
    [OK] 1.20 ms (0.00 min)
  ...
[5/5] test_1000000.json
  Running dp_bottomup...
    [OK] 350000.00 ms (5.83 min)
  ...

Resumed: 3 test cases skipped (already completed)
```

## Tips for Large Runs (1 Million Nodes)

### 1. Check Progress Periodically
```bash
# Check log file
tail -f overnight_log.txt

# Check CSV for completed results
wc -l results/overnight_benchmark_results.csv
```

### 2. Save Incrementally
- Script saves results after each test case
- Even if interrupted, partial results are saved
- CSV is updated continuously

### 3. Resume is Safe
- Won't lose existing results
- Only runs missing benchmarks
- Merges old and new data

### 4. Multiple Interruptions OK
- Can interrupt and resume multiple times
- Each resume continues from last saved state
- No data loss

## Troubleshooting Resume

### Problem: Script Re-runs Everything
**Solution**: Check if CSV file exists and has correct format
```bash
# Verify CSV exists
ls -la results/overnight_benchmark_results.csv

# Check format
head results/overnight_benchmark_results.csv
```

### Problem: Partial Results Not Detected
**Solution**: Script only skips if ALL 4 solutions have status. If one is missing, it will re-run that test case.

### Problem: Want to Re-run Specific Test
**Solution**: 
1. Open CSV file
2. Delete the row for that test case
3. Re-run script

## Best Practices

1. **Don't Delete CSV** - It contains your progress
2. **Check Log File** - See what was completed
3. **Backup Before Force Re-run** - Save CSV before deleting
4. **Let It Complete** - Resume handles interruptions automatically

## Summary

**To resume after interruption:**
1. Just run the same command again
2. Script automatically detects completed work
3. Only runs missing benchmarks
4. Merges results automatically

**No manual intervention needed!** 🎉

