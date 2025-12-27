# AI Threat Hunting Query Generation & Evaluation System

An AI-powered system that translates natural language threat hunting hypotheses into executable SQL queries for CloudTrail log analysis, with comprehensive evaluation metrics and explainable outputs.

## 🎯 Overview

This system addresses the challenge of automating threat hunting by:
- **Generating** SQL queries from natural language hypotheses using LLM (GPT-4)
- **Evaluating** query quality and result accuracy against expected outcomes
- **Explaining** the reasoning behind each generated query with confidence scores

## 🏗️ Architecture

```
┌─────────────────────┐
│   Hypotheses JSON   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Query Generator    │◄─── OpenAI GPT-4
│  (LLM-based)        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Generated Queries  │
│     (SQL/JSON)      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐      ┌──────────────────┐
│   Query Evaluator   │◄─────┤ CloudTrail Data  │
│                     │      │   (DuckDB)       │
└──────────┬──────────┘      └──────────────────┘
           │                          ▲
           │                          │
           ▼                          │
┌─────────────────────┐              │
│ Expected Outcomes   │──────────────┘
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Evaluation Report   │
│  (Metrics + JSON)   │
└─────────────────────┘
```

## ✨ Features

### Core Features
- **LLM-Based Query Generation**: Uses GPT-4 with chain-of-thought reasoning
- **Comprehensive Evaluation**: Precision, Recall, F1-Score, and custom metrics
- **Explainable Outputs**: Detailed reasoning for each generated query
- **Confidence Scoring**: Automatic assessment of query quality
- **Batch Processing**: Generate and evaluate multiple queries efficiently

### Advanced Features
- **Query Validation**: Syntax checking before execution
- **Error Handling**: Graceful degradation with informative error messages
- **Iteration Tracking**: Compare improvements across multiple runs
- **Flexible Backend**: DuckDB for fast in-memory query execution
- **Markdown Reports**: Human-readable evaluation reports

## 📋 Requirements

- Python 3.9+
- OpenAI API key
- CloudTrail dataset (nineteenFeaturesDf.csv)

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or navigate to the project directory
cd threat-hunting-query-system

# Install dependencies
pip install -r requirements.txt

# OR using Poetry
poetry install
```

### 2. Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your OpenAI API key
export OPENAI_API_KEY='your-api-key-here'
```

### 3. Download Data

Download the CloudTrail dataset from Kaggle:
- **Dataset**: [AWS CloudTrail Dataset from flaws.cloud](https://www.kaggle.com/datasets/nobukim/aws-cloudtrails-dataset-from-flaws-cloud)
- **File needed**: `nineteenFeaturesDf.csv`
- **Place in**: `./data/` directory

```bash
# Create data directory
mkdir -p data

# After downloading from Kaggle, move file to data/
mv ~/Downloads/nineteenFeaturesDf.csv data/

# Verify it's there
ls -lh data/nineteenFeaturesDf.csv
```

**Alternative: Generate Synthetic Data** (For Testing Without Kaggle Account)
```bash
python3 synthetic_data_generator.py --num-records 1000 --output data/nineteenFeaturesDf.csv
```

### 4. Run the System

```bash
# Full pipeline: generate queries + evaluate
python main.py --data data/nineteenFeaturesDf.csv

# Skip query generation and use existing queries
python main.py --data data/nineteenFeaturesDf.csv --skip-generation

# Use different model
python main.py --data data/nineteenFeaturesDf.csv --model gpt-4-turbo

# Specify iteration number (for tracking improvements)
python main.py --data data/nineteenFeaturesDf.csv --iteration 2
```

### 5. View Results

After running, check the `output/` directory:
- `generated_queries.json` - Generated SQL queries with explanations
- `evaluation_results_iter1.json` - Detailed evaluation metrics
- `EVALUATION_REPORT_ITER1.md` - Human-readable report

## 📁 Project Structure

```
threat-hunting-query-system/
├── query_generator.py      # LLM-based query generation
├── evaluator.py            # Evaluation framework
├── main.py                 # Main entry point
├── utils.py                # Helper functions
├── requirements.txt        # Python dependencies
├── pyproject.toml         # Poetry configuration
├── .env.example           # Environment template
├── README.md              # This file
├── APPROACH.md            # Methodology documentation
├── Dockerfile             # Container configuration
├── docker-compose.yml     # Multi-container setup
├── demo.ipynb             # Interactive Jupyter demo
├── output/                # Generated outputs
│   ├── generated_queries.json
│   ├── evaluation_results_iter1.json
│   └── EVALUATION_REPORT_ITER1.md
└── data/                  # Data directory
    └── nineteenFeaturesDf.csv
```

## 🔍 Component Details

### Query Generator (`query_generator.py`)

Generates SQL queries from hypotheses using GPT-4:

```python
from query_generator import QueryGenerator, load_hypotheses

# Initialize generator
generator = QueryGenerator(api_key="your-key", model="gpt-4o")

# Load hypotheses
hypotheses = load_hypotheses("hypotheses.json")

# Generate queries
queries = generator.generate_batch(hypotheses)

# Save results
generator.save_queries(queries, "generated_queries.json")
```

**Features:**
- Chain-of-thought reasoning
- CloudTrail schema awareness
- Structured JSON output
- Confidence scoring
- Error recovery

### Evaluator (`evaluator.py`)

Evaluates query quality and results:

```python
from evaluator import QueryEvaluator
from utils import load_hypotheses_outcomes

# Initialize evaluator with data
evaluator = QueryEvaluator("data/nineteenFeaturesDf.csv")

# Load generated queries and expected outcomes
with open("generated_queries.json") as f:
    queries = json.load(f)
expected = load_hypotheses_outcomes("hypotheses_outcomes.json")

# Run evaluation
report = evaluator.evaluate_batch(queries, expected)

# Print and save results
evaluator.print_summary(report)
evaluator.save_evaluation(report, "evaluation_results.json")
```

**Metrics:**
- **Precision**: Fraction of returned records that are correct
- **Recall**: Fraction of expected records that are found
- **F1 Score**: Harmonic mean of precision and recall
- **Exact Match Rate**: Percentage of perfectly matched records
- **Query Validity**: Syntax and execution success

## 🎨 Usage Examples

### Example 1: Generate Single Query

```python
from query_generator import QueryGenerator

generator = QueryGenerator()

hypothesis = {
    "id": "1",
    "name": "Failed Console Logins",
    "hypothesis": "CloudTrail logs contain failed console login attempts"
}

query = generator.generate_query(hypothesis)
print(query.sql_query)
print(f"Confidence: {query.explanation.confidence_score}")
```

### Example 2: Evaluate Specific Hypothesis

```python
from evaluator import QueryEvaluator

evaluator = QueryEvaluator("data/nineteenFeaturesDf.csv")

result = evaluator.evaluate_hypothesis(
    hypothesis_id="1",
    hypothesis_name="Failed Console Logins",
    sql_query="SELECT * FROM cloudtrail_logs WHERE eventName='ConsoleLogin' AND errorMessage IS NOT NULL",
    expected_results=expected_df
)

print(f"F1 Score: {result.f1_score:.3f}")
```

## 🐳 Docker Support

### Build and Run with Docker

```bash
# Build image
docker build -t threat-hunting-system .

# Run container
docker run -it --rm \
  -e OPENAI_API_KEY="your-key" \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/output:/app/output \
  threat-hunting-system

# OR use Docker Compose
docker-compose up
```

### Docker Compose

```bash
# Start all services
docker-compose up

# Run specific service
docker-compose run query-generator
docker-compose run evaluator

# View logs
docker-compose logs -f
```

## 📊 Evaluation Metrics Explained

### Precision
- **Definition**: Of all records returned by the query, what percentage are correct?
- **Formula**: `TP / (TP + FP)`
- **Interpretation**: High precision = few false positives

### Recall
- **Definition**: Of all expected records, what percentage did we find?
- **Formula**: `TP / (TP + FN)`
- **Interpretation**: High recall = few missed records

### F1 Score
- **Definition**: Harmonic mean of precision and recall
- **Formula**: `2 * (P * R) / (P + R)`
- **Interpretation**: Balanced measure of accuracy

### Overall Score
- **Formula**: `0.3 * Precision + 0.3 * Recall + 0.4 * F1`
- **Interpretation**: Weighted metric emphasizing F1 score

## 🔧 Configuration

### Environment Variables

```bash
# Required
export OPENAI_API_KEY="sk-..."

# Optional
export OPENAI_MODEL="gpt-4o"  # or gpt-4-turbo, gpt-4, etc.
```

### Command Line Arguments

```bash
python main.py \
  --hypotheses path/to/hypotheses.json \
  --outcomes path/to/outcomes.json \
  --data path/to/cloudtrail.csv \
  --output-dir ./my_output \
  --model gpt-4-turbo \
  --iteration 2 \
  --skip-generation  # Use existing queries
```

## 🧪 Testing

```bash
# Run unit tests
pytest

# With coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_query_generator.py
```

## 📈 Iteration & Improvement

The system supports iterative improvement:

1. **Baseline Run** (Iteration 1)
   ```bash
   python main.py --data data/nineteenFeaturesDf.csv --iteration 1
   ```

2. **Analyze Results**
   - Review `EVALUATION_REPORT_ITER1.md`
   - Identify low-performing hypotheses
   - Note common failure patterns

3. **Improve System**
   - Refine prompts in `query_generator.py`
   - Add validation logic
   - Enhance error handling

4. **Re-run** (Iteration 2)
   ```bash
   python main.py --data data/nineteenFeaturesDf.csv --iteration 2
   ```

5. **Compare**
   - Compare `evaluation_results_iter1.json` vs `iter2`
   - Track metrics improvements
   - Document in `APPROACH.md`

## 🎓 How to Extend

### Add New Data Sources

1. Modify `evaluator.py` to support new schemas
2. Update `_get_cloudtrail_schema()` in `query_generator.py`
3. Create new table in DuckDB

### Use Different LLM

```python
# Custom model
generator = QueryGenerator(model="gpt-4-turbo-preview")

# Or use Azure OpenAI
from openai import AzureOpenAI
# Modify QueryGenerator.__init__ accordingly
```

### Add Custom Metrics

```python
# In evaluator.py
def custom_metric(expected: pd.DataFrame, actual: pd.DataFrame) -> float:
    # Your logic here
    return score

# Add to evaluate_hypothesis()
```

## 🐛 Troubleshooting

### Issue: "OPENAI_API_KEY not set"
**Solution**: Export your API key: `export OPENAI_API_KEY='sk-...'`

### Issue: "File not found: nineteenFeaturesDf.csv"
**Solution**: Download dataset from Kaggle and place in `data/` directory

### Issue: "Query execution failed"
**Solution**: Check `generated_queries.json` for SQL syntax errors. Try re-generating with lower temperature.

### Issue: Low F1 scores
**Solution**: 
- Check if CloudTrail data matches expected schema
- Review generated queries for correctness
- Adjust prompts for better query generation

## 📚 Additional Resources

- [AWS CloudTrail Documentation](https://docs.aws.amazon.com/cloudtrail/)
- [DuckDB SQL Reference](https://duckdb.org/docs/sql/introduction)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Assignment Reference Article](https://medium.com/@gfekkas) - George Fekkas' threat hunting patterns

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional evaluation metrics
- Multi-step reasoning for complex queries
- Query optimization suggestions
- Support for other log formats (VPC Flow Logs, GuardDuty, etc.)
- Web UI improvements

## 📄 License

MIT License - see LICENSE file for details

## 👤 Author

Created for AiStrike AI Engineer Assignment

## 🙏 Acknowledgments

- George Fekkas for threat hunting reference material
- flaws.cloud for CloudTrail dataset
- OpenAI for GPT-4 API

---

**Need Help?** Check `APPROACH.md` for detailed methodology or open an issue.

