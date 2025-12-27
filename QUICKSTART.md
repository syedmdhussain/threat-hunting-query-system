# Quick Start Guide - 5 Minutes to Running System

## Prerequisites Check

Before starting, ensure you have:
- [ ] Python 3.9+ installed (`python --version`)
- [ ] OpenAI API key
- [ ] CloudTrail dataset downloaded from Kaggle

## Step 1: Installation (2 minutes)

```bash
# Navigate to project
cd threat-hunting-query-system

# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configuration (1 minute)

```bash
# Set your OpenAI API key
export OPENAI_API_KEY='sk-your-actual-api-key-here'
```

## Step 3: Prepare Data (1 minute)

Download CloudTrail data from Kaggle: https://www.kaggle.com/datasets/nobukim/aws-cloudtrails-dataset-from-flaws-cloud

```bash
# Create data directory
mkdir -p data

# Move downloaded file
mv ~/Downloads/nineteenFeaturesDf.csv data/

# Verify it's there
ls -lh data/nineteenFeaturesDf.csv
```

**Alternative (No Kaggle Account)**: Generate synthetic data
```bash
python3 synthetic_data_generator.py --num-records 1000 --output data/nineteenFeaturesDf.csv
```

## Step 4: Run the System (1-2 minutes)

```bash
# Run the complete pipeline
python main.py --data data/nineteenFeaturesDf.csv
```

You'll see output like:
```
================================================================================
AI THREAT HUNTING QUERY GENERATION & EVALUATION SYSTEM
================================================================================

Configuration:
  Hypotheses: ../assignment/hypotheses.json
  Expected Outcomes: ../assignment/hypotheses_outcomes.json
  CloudTrail Data: data/nineteenFeaturesDf.csv
  Output Directory: ./output
  Model: gpt-4o

[STEP 1] Loading hypotheses...
Loaded 11 hypotheses

[STEP 2] Generating SQL queries from hypotheses...
Generating query 1/11: Sign-in Failures (Brute Force/Bot Attacks)
Generating query 2/11: Root Access Through Console
...
```

## Step 5: View Results (30 seconds)

```bash
# Check generated files
ls -la output/

# View the markdown report
cat output/EVALUATION_REPORT_ITER1.md

# Or open in your editor
open output/EVALUATION_REPORT_ITER1.md  # macOS
```

## Expected Output Files

After completion, you should have:

```
output/
├── generated_queries.json           # All queries with explanations
├── evaluation_results_iter1.json    # Detailed metrics (JSON)
└── EVALUATION_REPORT_ITER1.md       # Human-readable report
```

## What You'll See

### Console Output Summary:
```
EVALUATION SUMMARY
================================================================================

Total Hypotheses: 11
Successful Queries: 9
Failed Queries: 2

Average Metrics:
  Precision: 0.723
  Recall:    0.681
  F1 Score:  0.701
  Overall:   0.695
```

### Example Query Generated:

**Hypothesis**: "CloudTrail logs contain failed console login attempts"

**Generated SQL**:
```sql
SELECT eventTime, sourceIPAddress, errorMessage, userIdentityuserName
FROM cloudtrail_logs
WHERE eventName = 'ConsoleLogin'
  AND errorMessage IS NOT NULL
ORDER BY eventTime DESC
```

**Explanation**:
- Interpretation: "Detecting brute force login attempts by filtering failed console logins"
- Reasoning: "ConsoleLogin events with errorMessage indicate failures"
- Confidence: 92%

## Troubleshooting Quick Fixes

### Problem: "OPENAI_API_KEY not set"
```bash
export OPENAI_API_KEY='your-key'
```

### Problem: "File not found: nineteenFeaturesDf.csv"
```bash
# Make sure file is in data/ directory
ls data/nineteenFeaturesDf.csv
```

### Problem: "ModuleNotFoundError"
```bash
# Make sure venv is activated
source venv/bin/activate
pip install -r requirements.txt
```

## Next Steps

Now that it's working:

1. **Explore the Notebook** for interactive demo:
   ```bash
   jupyter notebook demo.ipynb
   ```

2. **Read the Reports** to understand results:
   ```bash
   cat output/EVALUATION_REPORT_ITER1.md
   ```

3. **Iterate and Improve**:
   ```bash
   # Make improvements to prompts
   # Run again with iteration 2
   python main.py --data data/nineteenFeaturesDf.csv --iteration 2
   ```

4. **Extend to New Data** - See README.md section "How to Extend"

## Common Commands

```bash
# Run with different model
python main.py --data data/nineteenFeaturesDf.csv --model gpt-4-turbo

# Skip query generation (use existing)
python main.py --data data/nineteenFeaturesDf.csv --skip-generation

# Custom output directory
python main.py --data data/nineteenFeaturesDf.csv --output-dir ./my_results

# See all options
python main.py --help
```

## Docker Alternative

If you prefer Docker:

```bash
# Build image
docker build -t threat-hunting .

# Run
docker run -it --rm \
  -e OPENAI_API_KEY="your-key" \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/output:/app/output \
  threat-hunting \
  python main.py --data /app/data/nineteenFeaturesDf.csv
```

## Success Indicators

✅ All steps completed without errors  
✅ Console shows "PIPELINE COMPLETE!"  
✅ Output directory has 3 files  
✅ Success rate >= 80%  
✅ Average F1 score >= 0.60  

## Getting Help

- Detailed docs: `README.md`
- Installation help: `INSTALL.md`
- Methodology: `APPROACH.md`
- Full solution: `SOLUTION_SUMMARY.md`

---

**Total Time**: ~5 minutes  
**Next**: Explore `demo.ipynb` for interactive demo!

🎉 **Congratulations! You're now running an AI-powered threat hunting system!**

