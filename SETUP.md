# Setup Guide

## Quick Setup (5 minutes)

### 1. Install Dependencies

```bash
# Create virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 2. Configure API Key

```bash
# Set environment variable
export OPENAI_API_KEY='your-openai-api-key-here'

# Or create .env file
echo "OPENAI_API_KEY=your-key-here" > .env
```

Get your API key from: https://platform.openai.com/api-keys

### 3. Prepare Data

**Option A: Use Synthetic Data (Quick Testing)**
```bash
python3 synthetic_data_generator.py --num-records 1000 --output data/cloudtrail.csv
```

**Option B: Download Real CloudTrail Data**
1. Go to: https://www.kaggle.com/datasets/nobukim/aws-cloudtrails-dataset-from-flaws-cloud
2. Download `nineteenFeaturesDf.csv`
3. Place in `data/` directory

### 4. Run the System

```bash
python3 main.py --data data/cloudtrail.csv
```

## Detailed Setup

### Prerequisites

- Python 3.9 or higher
- pip package manager
- 2GB RAM minimum (8GB recommended)
- OpenAI API key with credits

### Installation Methods

#### Method 1: pip (Recommended)

```bash
pip install -r requirements.txt
```

#### Method 2: Poetry

```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Activate environment
poetry shell
```

#### Method 3: Docker

```bash
# Build image
docker build -t threat-hunting-system .

# Run
docker run -it --rm \
  -e OPENAI_API_KEY="your-key" \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/output:/app/output \
  threat-hunting-system
```

### Verification

Test your installation:

```bash
# Test imports
python3 -c "from query_generator import QueryGenerator; from evaluator import QueryEvaluator; print('✓ Installation successful')"

# Run unit tests
pytest test_system.py -v

# Generate sample data and test
python3 synthetic_data_generator.py --num-records 100 --output test.csv
python3 main.py --data test.csv
```

## Configuration

### Environment Variables

```bash
# Required
export OPENAI_API_KEY='sk-your-key-here'

# Optional
export OPENAI_MODEL='gpt-4o'  # or gpt-4-turbo, gpt-4
```

### Command Line Options

```bash
python3 main.py [OPTIONS]

Options:
  --data PATH              Path to CloudTrail CSV file (required)
  --hypotheses PATH        Path to hypotheses JSON (default: ../assignment/hypotheses.json)
  --outcomes PATH          Path to outcomes JSON (default: ../assignment/hypotheses_outcomes.json)
  --output-dir PATH        Output directory (default: ./output)
  --model MODEL            OpenAI model (default: gpt-4o)
  --iteration N            Iteration number for tracking (default: 1)
  --skip-generation        Use existing queries, skip generation
  --help                   Show help message
```

## Troubleshooting

### Issue: ModuleNotFoundError

**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: OPENAI_API_KEY not set

**Solution**: Set environment variable
```bash
export OPENAI_API_KEY='your-key'
```

### Issue: Insufficient API quota

**Solution**: Add credits to your OpenAI account
- Go to: https://platform.openai.com/account/billing
- Add payment method and credits
- Minimum $5 recommended

### Issue: CSV parsing error

**Solution**: Use all_varchar mode (already configured in evaluator.py)
- System automatically handles mixed data types
- If issues persist, check CSV file integrity

### Issue: Out of memory

**Solution**: 
- Use smaller dataset for testing
- Increase system RAM
- Use Docker with memory limits

## Data Requirements

### CloudTrail CSV Schema

Required columns:
- eventTime
- eventName
- eventSource
- sourceIPAddress
- userAgent
- errorCode
- errorMessage
- awsRegion
- userIdentitytype
- userIdentityuserName
- (and 9 more - see sample_queries.json)

### Sample Data

Generate test data:
```bash
# Small dataset (100 records)
python3 synthetic_data_generator.py --num-records 100 --output small.csv

# Medium dataset (1000 records) 
python3 synthetic_data_generator.py --num-records 1000 --output medium.csv

# Large dataset (10000 records)
python3 synthetic_data_generator.py --num-records 10000 --output large.csv
```

## Development Setup

### For Development/Testing

```bash
# Install with dev dependencies
pip install -r requirements.txt pytest pytest-cov

# Run tests with coverage
pytest --cov=. --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Code Style

```bash
# Format code
black *.py

# Lint
flake8 *.py

# Type check
mypy *.py
```

## Docker Setup

### Build Image

```bash
docker build -t threat-hunting-system .
```

### Run with Docker Compose

```bash
# Start all services
docker-compose up

# Run specific service
docker-compose run query-generator

# Stop services
docker-compose down
```

## Performance Optimization

### For Large Datasets

```bash
# Use batch processing (already optimized in code)
# DuckDB handles 2M+ records efficiently

# Monitor memory usage
python3 -m memory_profiler main.py --data large_data.csv
```

### API Cost Optimization

```bash
# Generate queries once, reuse for evaluation
python3 main.py --data data.csv --iteration 1

# Skip regeneration in future runs
python3 main.py --data data.csv --skip-generation
```

## Next Steps

After setup:

1. **Test with synthetic data**
   ```bash
   python3 synthetic_data_generator.py --num-records 1000 --output test.csv
   python3 main.py --data test.csv
   ```

2. **Download real CloudTrail data** from Kaggle

3. **Run full evaluation**
   ```bash
   python3 main.py --data data/nineteenFeaturesDf.csv
   ```

4. **Review results** in `output/` directory

## Support

- Check README.md for overview
- Review sample_queries.json for examples
- Run `pytest test_system.py` to verify installation
- Open GitHub issue for bugs

---

**Setup Time**: 5-10 minutes  
**First Run**: 2-3 minutes with API key  
**System Status**: Production-ready

