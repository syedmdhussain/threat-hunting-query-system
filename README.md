# AI Threat Hunting Query Generation System

AI-powered system that translates natural language threat hunting hypotheses into executable SQL queries for CloudTrail log analysis, using GPT-4 with comprehensive evaluation framework.

## 🎯 Overview

This system addresses the challenge of automating threat hunting by:
- **Generating** SQL queries from natural language hypotheses using GPT-4
- **Executing** queries against CloudTrail logs using DuckDB
- **Evaluating** query quality with Precision, Recall, and F1 metrics
- **Explaining** reasoning with confidence scores and assumptions

## ✨ Key Features

- **LLM-Based Query Generation**: GPT-4 with chain-of-thought reasoning
- **Production-Ready**: Handles 2M+ CloudTrail events efficiently
- **Comprehensive Evaluation**: Multiple metrics (P/R/F1) with detailed analysis
- **Explainable AI**: Full transparency in query generation decisions
- **Docker Support**: Containerized deployment ready
- **Synthetic Data Generator**: Test without Kaggle account

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- **OpenAI API key with credits** (required for query generation)
  - Get key from: https://platform.openai.com/api-keys
  - Add credits at: https://platform.openai.com/account/billing
  - Cost: ~$0.15-0.20 for all 11 queries
- CloudTrail dataset (or use synthetic data generator)

### Installation

```bash
# Clone repository
git clone https://github.com/syedmdhussain/threat-hunting-query-system.git
cd threat-hunting-query-system

# Install dependencies
pip install -r requirements.txt

# Set API key
export OPENAI_API_KEY='your-key-here'

# Generate sample data (or download from Kaggle)
python3 synthetic_data_generator.py --num-records 1000 --output data/cloudtrail.csv

# Run the system
python3 main.py --data data/cloudtrail.csv
```

### Using Real CloudTrail Data

Download from Kaggle: https://www.kaggle.com/datasets/nobukim/aws-cloudtrails-dataset-from-flaws-cloud

```bash
mkdir -p data
mv ~/Downloads/nineteenFeaturesDf.csv data/
python3 main.py --data data/nineteenFeaturesDf.csv
```

## ⚠️ Important Note

**OpenAI API Key Required:** This system uses GPT-4 to generate SQL queries. You need an active OpenAI API key with credits ($5 minimum recommended).

**Alternative:** Pre-generated sample queries are included in `sample_queries.json` for testing without API credits.

## 📊 Results

Successfully processed **1.9 million CloudTrail events** with:

- **Query Success Rate**: 91% (10/11 queries executed)
- **Perfect Accuracy**: 100% on failed login detection (12/12 events)
- **Perfect Accuracy**: 100% on root access detection (61/61 events)
- **Processing Time**: ~30 seconds for 2M records

### Threats Detected
From real CloudTrail data analysis:
- 12 failed login attempts (brute force indicators)
- 61 root user console logins (high-risk access)
- 4 CloudTrail disruption attempts
- 2,387 unauthorized API calls
- 4,767 reconnaissance attempts (GetCallerIdentity)
- 1,896 suspicious user agent requests

## 🏗️ Architecture

```
Input: Natural Language Hypotheses
          ↓
   Query Generator (GPT-4)
   • Chain-of-thought reasoning
   • Schema-aware generation
   • Confidence scoring
          ↓
   Query Executor (DuckDB)
   • In-memory processing
   • 2M+ event handling
          ↓
   Evaluator
   • Precision/Recall/F1
   • Set-based comparison
          ↓
   Output: Reports + Metrics
```

## 📁 Project Structure

```
threat-hunting-query-system/
├── query_generator.py          # LLM-based query generation
├── evaluator.py                # Evaluation framework
├── main.py                     # Pipeline orchestration
├── utils.py                    # Helper functions
├── synthetic_data_generator.py # Data generation
├── test_system.py              # Unit tests
├── requirements.txt            # Dependencies
├── Dockerfile                  # Container config
└── README.md                   # This file
```

## 🔧 Usage

### Basic Usage

```bash
python3 main.py --data data/cloudtrail.csv
```

### Advanced Options

```bash
# Use different model
python3 main.py --data data/cloudtrail.csv --model gpt-4-turbo

# Skip query generation (use existing)
python3 main.py --data data/cloudtrail.csv --skip-generation

# Specify iteration for tracking improvements
python3 main.py --data data/cloudtrail.csv --iteration 2

# Custom output directory
python3 main.py --data data/cloudtrail.csv --output-dir ./results
```

### Output Files

After running, check `output/` directory:
- `generated_queries.json` - SQL queries with explanations
- `evaluation_results_iter1.json` - Detailed metrics
- `EVALUATION_REPORT_ITER1.md` - Human-readable report

## 🐳 Docker Deployment

```bash
# Build image
docker build -t threat-hunting-system .

# Run container
docker run -it --rm \
  -e OPENAI_API_KEY="your-key" \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/output:/app/output \
  threat-hunting-system \
  python3 main.py --data /app/data/cloudtrail.csv
```

## 📈 Evaluation Metrics

- **Precision**: Fraction of returned records that are correct
- **Recall**: Fraction of expected records found
- **F1 Score**: Harmonic mean of precision and recall
- **Query Validity**: Syntactic correctness and execution success

## 🧪 Testing

```bash
# Run unit tests
pytest test_system.py

# Generate synthetic data for testing
python3 synthetic_data_generator.py --num-records 1000 --output test_data.csv

# Test with synthetic data
python3 main.py --data test_data.csv
```

## 🎯 Assignment Requirements Met

✅ Query generation system using LLM  
✅ Comprehensive evaluation framework  
✅ Explainable outputs with reasoning  
✅ Works with CloudTrail dataset  
✅ Multiple evaluation metrics  
✅ Iteration tracking and improvement  
✅ Complete documentation  
✅ Docker support (bonus)  
✅ Unit tests (bonus)  

## 🔍 Example Query Generation

**Input Hypothesis:**
> "CloudTrail logs contain failed console login attempts that could indicate brute force attacks"

**Generated SQL:**
```sql
SELECT eventTime, sourceIPAddress, errorMessage, userIdentityuserName, awsRegion 
FROM cloudtrail_logs 
WHERE eventName = 'ConsoleLogin' AND errorMessage IS NOT NULL 
ORDER BY eventTime DESC
```

**Explanation:**
- **Interpretation**: Detecting brute force login attempts by identifying failed AWS console logins
- **Reasoning**: ConsoleLogin events with errorMessage indicate authentication failures
- **Confidence**: 92%
- **Key Fields**: eventName, errorMessage, sourceIPAddress

## 📚 Technical Stack

- **Language**: Python 3.9+
- **LLM**: OpenAI GPT-4o
- **Database**: DuckDB (in-memory)
- **Data Processing**: pandas, numpy
- **Evaluation**: scikit-learn
- **Containerization**: Docker
- **Testing**: pytest

## 🛠️ System Requirements

- **Minimum**: 2GB RAM, 2 CPU cores
- **Recommended**: 8GB RAM, 4 CPU cores
- **Storage**: 5GB (for CloudTrail data)
- **OS**: macOS, Linux, Windows (with WSL2)

## 📝 License

MIT License - See LICENSE file for details

## 👤 Author

Syed Mohammad Hussain  
https://github.com/syedmdhussain

## 🙏 Acknowledgments

- Assignment by AiStrike
- CloudTrail dataset from flaws.cloud
- OpenAI GPT-4 API

## 📞 Support

For questions or issues:
- Open an issue on GitHub
- Review the code documentation
- Check the sample_queries.json for examples

---

**Status**: Production-ready, tested on 1.9M CloudTrail events  
**Performance**: 91% query success rate, 100% accuracy on critical threats  
**Last Updated**: December 2024
