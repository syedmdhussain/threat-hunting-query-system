# Kaggle CLI Setup for Automated Dataset Download

## Quick Setup

### 1. Install Kaggle CLI

```bash
pip install kaggle
```

### 2. Get API Credentials

1. Go to https://kaggle.com/settings
2. Scroll to "API" section
3. Click "Create New API Token"
4. A file `kaggle.json` will download

### 3. Configure Credentials

```bash
# Create kaggle directory
mkdir -p ~/.kaggle

# Move credentials file
mv ~/Downloads/kaggle.json ~/.kaggle/

# Set permissions (important!)
chmod 600 ~/.kaggle/kaggle.json
```

### 4. Verify Setup

```bash
# Test authentication
kaggle datasets list

# Should show list of datasets
```

## Download CloudTrail Dataset

```bash
# Download the dataset
kaggle datasets download -d nobukim/aws-cloudtrails-dataset-from-flaws-cloud

# Extract to data directory
unzip aws-cloudtrails-dataset-from-flaws-cloud.zip -d data/

# Verify
ls -lh data/nineteenFeaturesDf.csv
```

## One-Line Download

```bash
kaggle datasets download -d nobukim/aws-cloudtrails-dataset-from-flaws-cloud && unzip aws-cloudtrails-dataset-from-flaws-cloud.zip -d data/ && rm aws-cloudtrails-dataset-from-flaws-cloud.zip
```

## Troubleshooting

### Issue: "Could not find kaggle.json"

**Solution**: Ensure file is in correct location
```bash
ls ~/.kaggle/kaggle.json
# Should exist

# If not, move it there:
mv ~/Downloads/kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```

### Issue: "403 Forbidden"

**Solution**: Accept dataset terms on Kaggle website
1. Visit https://www.kaggle.com/datasets/nobukim/aws-cloudtrails-dataset-from-flaws-cloud
2. Click "Download" once (accepts terms)
3. Then run kaggle CLI command

### Issue: "401 Unauthorized"

**Solution**: Regenerate API token
1. Go to kaggle.com/settings
2. Delete old API token
3. Create new token
4. Replace ~/.kaggle/kaggle.json

### Issue: Permission denied

**Solution**: Fix file permissions
```bash
chmod 600 ~/.kaggle/kaggle.json
```

## Alternative: Use Python API

```python
import kagglehub

# Download dataset
path = kagglehub.dataset_download("nobukim/aws-cloudtrails-dataset-from-flaws-cloud")
print(f"Dataset downloaded to: {path}")
```

## For Windows Users

```powershell
# Install
pip install kaggle

# Create directory
mkdir $env:USERPROFILE\.kaggle

# Move credentials
move $env:USERPROFILE\Downloads\kaggle.json $env:USERPROFILE\.kaggle\

# Download dataset
kaggle datasets download -d nobukim/aws-cloudtrails-dataset-from-flaws-cloud

# Extract
Expand-Archive aws-cloudtrails-dataset-from-flaws-cloud.zip -DestinationPath data\
```

## No Kaggle Account?

Use the synthetic data generator:

```bash
python3 synthetic_data_generator.py \
  --num-records 1000 \
  --output data/nineteenFeaturesDf.csv
```

---

**Ready!** Now run: `python3 main.py --data data/nineteenFeaturesDf.csv`

