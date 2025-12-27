#!/usr/bin/env python3
"""
Quick Demo of the Threat Hunting System
Demonstrates the system without requiring OpenAI API key
"""

import pandas as pd
import json
from pathlib import Path

print("="*80)
print("AI THREAT HUNTING QUERY GENERATION SYSTEM - DEMO")
print("="*80)

# Step 1: Load and display hypotheses
print("\n[STEP 1] Loading Threat Hunting Hypotheses\n")
print("-"*80)

with open('../assignment/hypotheses.json', 'r') as f:
    hypotheses = json.load(f)

print(f"Total hypotheses: {len(hypotheses)}\n")

for h in hypotheses[:3]:  # Show first 3
    print(f"[{h['id']}] {h['name']}")
    print(f"    Hypothesis: {h['hypothesis']}")
    print()

print(f"... and {len(hypotheses) - 3} more\n")

# Step 2: Show synthetic data
print("[STEP 2] Examining CloudTrail Data\n")
print("-"*80)

df = pd.read_csv('data/demo_cloudtrail.csv')
print(f"Total CloudTrail events: {len(df)}")
print(f"Date range: {df['eventTime'].min()} to {df['eventTime'].max()}")
print(f"\nTop event types:")
print(df['eventName'].value_counts().head(10))

# Step 3: Demonstrate query execution
print("\n[STEP 3] Demonstrating Query Execution\n")
print("-"*80)

from evaluator import QueryEvaluator

evaluator = QueryEvaluator('data/demo_cloudtrail.csv')

# Example queries matching hypotheses
example_queries = [
    {
        'id': '1',
        'name': 'Failed Console Logins',
        'query': """
            SELECT eventTime, sourceIPAddress, errorMessage, userIdentityuserName
            FROM cloudtrail_logs
            WHERE eventName = 'ConsoleLogin' AND errorMessage IS NOT NULL
            ORDER BY eventTime
        """
    },
    {
        'id': '3',
        'name': 'CloudTrail Disruption',
        'query': """
            SELECT eventTime, eventName, sourceIPAddress, userIdentityuserName
            FROM cloudtrail_logs
            WHERE eventName IN ('StopLogging', 'DeleteTrail')
            ORDER BY eventTime
        """
    },
    {
        'id': '6',
        'name': 'Secrets Manager Access',
        'query': """
            SELECT eventTime, eventName, sourceIPAddress, userAgent
            FROM cloudtrail_logs
            WHERE eventName = 'GetSecretValue'
            ORDER BY eventTime
        """
    }
]

for query_info in example_queries:
    print(f"\n📋 Hypothesis: {query_info['name']}")
    print(f"ID: {query_info['id']}")
    
    success, results, error = evaluator.execute_query(query_info['query'])
    
    if success:
        print(f"✓ Query executed successfully")
        print(f"✓ Found {len(results)} matching events")
        
        if len(results) > 0:
            print(f"\nSample results:")
            print(results.to_string(index=False, max_rows=5))
    else:
        print(f"✗ Query failed: {error}")
    
    print("-"*80)

# Step 4: Show what query generation looks like
print("\n[STEP 4] Query Generation Example\n")
print("-"*80)

print("""
For each hypothesis, the system uses GPT-4 to generate SQL queries.

Example for "Failed Console Logins":

INPUT:
  Hypothesis: "CloudTrail logs contain failed console login attempts"

GENERATED QUERY:
  SELECT eventTime, sourceIPAddress, errorMessage, userIdentityuserName
  FROM cloudtrail_logs
  WHERE eventName = 'ConsoleLogin' AND errorMessage IS NOT NULL
  ORDER BY eventTime DESC

EXPLANATION:
  - Interpretation: Detecting brute force login attempts
  - Reasoning: ConsoleLogin events with errorMessage indicate failures
  - Confidence: 0.92
  - Key Fields: eventName, errorMessage, sourceIPAddress

To run full query generation, you need an OpenAI API key:
  export OPENAI_API_KEY='your-key'
  python3 main.py --data data/demo_cloudtrail.csv
""")

# Step 5: Summary
print("\n[STEP 5] System Capabilities Summary\n")
print("="*80)

print("""
✅ WHAT THIS SYSTEM DOES:

1. QUERY GENERATION
   - Translates natural language hypotheses into SQL
   - Uses GPT-4 with chain-of-thought reasoning
   - Provides confidence scores and explanations

2. QUERY EXECUTION
   - Runs queries against CloudTrail data using DuckDB
   - Fast in-memory processing
   - Handles large datasets efficiently

3. EVALUATION
   - Compares results against expected outcomes
   - Calculates Precision, Recall, F1 Score
   - Generates detailed reports

4. EXPLAINABILITY
   - Every query includes reasoning
   - Assumptions clearly stated
   - Confidence scoring

📊 DATA STATISTICS:
   - CloudTrail Events: {events}
   - Unique Event Types: {event_types}
   - Date Range: {date_range}
   - Threat Events: ~{threats} (estimated)

📁 OUTPUT FILES (when run with API key):
   - generated_queries.json      - All SQL queries with explanations
   - evaluation_results.json     - Detailed metrics
   - EVALUATION_REPORT.md        - Human-readable report

🚀 TO RUN FULL SYSTEM:
   1. Set API key: export OPENAI_API_KEY='your-key'
   2. Run: python3 main.py --data data/demo_cloudtrail.csv
   3. Check output/ directory for results
""".format(
    events=len(df),
    event_types=df['eventName'].nunique(),
    date_range=f"{df['eventTime'].min().split('T')[0]} to {df['eventTime'].max().split('T')[0]}",
    threats=int(len(df) * 0.2)
))

print("="*80)
print("DEMO COMPLETE!")
print("="*80)

evaluator.close()

