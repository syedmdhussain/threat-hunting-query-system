# Installation Guide

## Prerequisites

- Python 3.9 or higher
- OpenAI API key
- CloudTrail dataset (nineteenFeaturesDf.csv)
- 2GB RAM minimum
- 5GB disk space (for data)

## Quick Install

### Option 1: pip (Recommended)

```bash
# Clone/navigate to project directory
cd threat-hunting-query-system

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OpenAI API key

# Verify installation
python -c "import pandas, duckdb, openai; print('✓ All dependencies installed')"
```

### Option 2: Poetry

```bash
# Install Poetry (if not already installed)
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Activate shell
poetry shell

# Configure environment
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### Option 3: Docker

```bash
# Build image
docker build -t threat-hunting-system .

# Run container
docker run -it --rm \
  -e OPENAI_API_KEY="your-key-here" \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/output:/app/output \
  threat-hunting-system \
  python main.py --data /app/data/nineteenFeaturesDf.csv
```

## Download Dataset

1. Go to Kaggle: https://www.kaggle.com/datasets/georgetakkas/cloudtrail-19-features
2. Download the dataset
3. Extract `nineteenFeaturesDf.csv`
4. Place in `data/` directory:

```bash
mkdir -p data
mv ~/Downloads/nineteenFeaturesDf.csv data/
```

## Configuration

### Set OpenAI API Key

**Option 1: Environment Variable** (Recommended)

```bash
export OPENAI_API_KEY='sk-your-key-here'
```

**Option 2: .env File**

```bash
cp .env.example .env
# Edit .env and add:
OPENAI_API_KEY=sk-your-key-here
```

**Option 3: Pass directly in code**

```python
generator = QueryGenerator(api_key='sk-your-key-here')
```

### Verify Configuration

```bash
python -c "import os; print('✓ API key set' if os.getenv('OPENAI_API_KEY') else '✗ API key missing')"
```

## Running the System

### Basic Usage

```bash
python main.py --data data/nineteenFeaturesDf.csv
```

### With Custom Options

```bash
python main.py \
  --data data/nineteenFeaturesDf.csv \
  --hypotheses ../assignment/hypotheses.json \
  --outcomes ../assignment/hypotheses_outcomes.json \
  --output-dir ./my_output \
  --model gpt-4o \
  --iteration 1
```

### Skip Query Generation (Use Existing)

```bash
python main.py --data data/nineteenFeaturesDf.csv --skip-generation
```

## Troubleshooting

### Issue: ModuleNotFoundError

**Solution**: Make sure virtual environment is activated and dependencies are installed

```bash
source venv/bin/activate  # or poetry shell
pip install -r requirements.txt
```

### Issue: OPENAI_API_KEY not set

**Solution**: Export the environment variable

```bash
export OPENAI_API_KEY='your-key-here'
```

### Issue: File not found: nineteenFeaturesDf.csv

**Solution**: Download and place in correct location

```bash
mkdir -p data
# Download from Kaggle and move:
mv ~/Downloads/nineteenFeaturesDf.csv data/
```

### Issue: Permission denied on output directory

**Solution**: Create directory with write permissions

```bash
mkdir -p output
chmod 755 output
```

### Issue: DuckDB connection error

**Solution**: Verify CSV file is valid and not corrupted

```bash
# Test with Python
python -c "import duckdb; duckdb.connect(':memory:').execute('SELECT 1')"
```

### Issue: Low F1 scores

**Possible causes**:
1. Data schema mismatch (check column names)
2. Wrong model selected (try gpt-4o or gpt-4-turbo)
3. Prompt needs tuning (see APPROACH.md)

## Testing

### Run Unit Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest

# With coverage
pytest --cov=. --cov-report=html
open htmlcov/index.html
```

### Quick Smoke Test

```bash
# Test imports
python -c "from query_generator import QueryGenerator; from evaluator import QueryEvaluator; print('✓ Imports OK')"

# Test on one hypothesis
python -c "
from query_generator import QueryGenerator, load_hypotheses
hypotheses = load_hypotheses('../assignment/hypotheses.json')
generator = QueryGenerator()
query = generator.generate_query(hypotheses[0])
print(f'✓ Generated query: {query.sql_query[:50]}...')
"
```

## Jupyter Notebook

### Launch Notebook

```bash
# Install Jupyter (if not already)
pip install jupyter notebook

# Launch
jupyter notebook demo.ipynb
```

### Or Use JupyterLab

```bash
pip install jupyterlab
jupyter lab
```

### Docker with Jupyter

```bash
docker-compose up jupyter
# Access at: http://localhost:8888
```

## Development Setup

### Install Dev Dependencies

```bash
# With pip
pip install -r requirements.txt
pip install pytest pytest-cov black flake8 mypy

# With Poetry
poetry install --with dev
```

### Code Formatting

```bash
# Format code
black *.py

# Lint
flake8 *.py

# Type check
mypy *.py
```

## Uninstall

### Remove Virtual Environment

```bash
deactivate
rm -rf venv/
```

### Remove Docker Images

```bash
docker rmi threat-hunting-system:latest
docker rmi threat-hunting-system:dev
```

### Clean Generated Files

```bash
rm -rf output/
rm -rf __pycache__/
rm -rf .pytest_cache/
```

## Next Steps

After installation:

1. Read `README.md` for usage guide
2. Review `APPROACH.md` for methodology
3. Run `python main.py --help` to see all options
4. Check `demo.ipynb` for interactive walkthrough
5. Explore generated outputs in `output/` directory

## Getting Help

- Check README.md for documentation
- Review APPROACH.md for implementation details
- Look at demo.ipynb for examples
- Check GitHub issues (if applicable)

## System Requirements

### Minimum

- CPU: 2 cores
- RAM: 2GB
- Disk: 5GB
- OS: macOS, Linux, Windows

### Recommended

- CPU: 4+ cores
- RAM: 8GB+
- Disk: 10GB+
- SSD storage

## Supported Platforms

- ✅ macOS (Intel & Apple Silicon)
- ✅ Linux (Ubuntu 20.04+, Debian 11+)
- ✅ Windows 10/11 with WSL2
- ✅ Windows 10/11 native
- ✅ Docker (all platforms)

## API Costs Estimate

Query generation uses OpenAI API:

- Model: GPT-4o
- Avg tokens per query: ~1,500
- Cost per query: ~$0.015
- Total for 11 hypotheses: ~$0.17

Use `--skip-generation` to avoid regenerating queries during development.

