# CloudTrail Dataset Download Instructions

## 📥 Quick Download Guide

### Method 1: Manual Download (Easiest)

1. **Visit Kaggle Dataset Page**
   - URL: https://www.kaggle.com/datasets/nobukim/aws-cloudtrails-dataset-from-flaws-cloud
   - Login to Kaggle (create free account if needed)

2. **Download the Dataset**
   - Click the "Download" button (top right)
   - File size: ~150-200MB (zipped)
   - Extract the downloaded ZIP file

3. **Place in Project**
   ```bash
   cd threat-hunting-query-system
   mkdir -p data
   mv ~/Downloads/nineteenFeaturesDf.csv data/
   ```

4. **Verify**
   ```bash
   ls -lh data/nineteenFeaturesDf.csv
   # Should see file ~150-200MB
   
   head -3 data/nineteenFeaturesDf.csv
   # Should see CSV headers and data
   ```

### Method 2: Kaggle CLI (Automated)

```bash
# Install Kaggle CLI
pip install kaggle

# Setup credentials
# 1. Go to kaggle.com/settings
# 2. Click "Create New API Token"
# 3. Save kaggle.json to ~/.kaggle/

# Download dataset
kaggle datasets download -d nobukim/aws-cloudtrails-dataset-from-flaws-cloud

# Extract
unzip aws-cloudtrails-dataset-from-flaws-cloud.zip -d data/

# Verify
ls -lh data/nineteenFeaturesDf.csv
```

### Method 3: Synthetic Data (No Kaggle Account Needed)

```bash
# Generate synthetic CloudTrail data
python3 synthetic_data_generator.py \
  --num-records 1000 \
  --output data/nineteenFeaturesDf.csv \
  --include-threats

# This creates realistic test data matching the schema
```

## 📊 Dataset Information

- **Source**: flaws.cloud CloudTrail logs
- **Format**: CSV
- **Size**: ~150-200 MB
- **Records**: ~160,000+ events
- **Time Range**: 2017-2020
- **Features**: 19 columns

### Expected Columns

```
eventTime, eventName, eventSource, sourceIPAddress, userAgent,
errorCode, errorMessage, awsRegion, userIdentitytype, 
userIdentityuserName, userIdentityarn, userIdentityaccountId,
requestParametersinstanceType, requestParametersbucketName,
responseElementsaccessKeyId, eventID, readOnly, resources,
recipientAccountId
```

## ✅ Verification Steps

After downloading, verify the data:

```bash
# Check file exists and size
ls -lh data/nineteenFeaturesDf.csv

# Count records (should be ~160k)
wc -l data/nineteenFeaturesDf.csv

# Check columns (should be 19)
head -1 data/nineteenFeaturesDf.csv | tr ',' '\n' | wc -l

# Preview data
head -10 data/nineteenFeaturesDf.csv

# Check for completeness
tail -10 data/nineteenFeaturesDf.csv
```

## 🐛 Troubleshooting

### Issue: "Kaggle requires authentication"

**Solution**: Create free Kaggle account
- Go to https://www.kaggle.com/
- Click "Register"
- Login and download

### Issue: "kaggle.json not found"

**Solution**: Create API credentials
```bash
# 1. Go to kaggle.com/settings
# 2. Scroll to "API" section
# 3. Click "Create New API Token"
# 4. Move kaggle.json to correct location:

mkdir -p ~/.kaggle
mv ~/Downloads/kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```

### Issue: "File too large / Slow download"

**Solution**: Use synthetic data generator
```bash
# Generates 1000 realistic records in seconds
python3 synthetic_data_generator.py --output data/nineteenFeaturesDf.csv
```

### Issue: "Cannot access Kaggle from corporate network"

**Solution**: Download at home or use synthetic data
- Corporate firewalls may block Kaggle
- Download on personal network
- Or use synthetic data generator

## 🎯 Ready to Run

Once data is in place:

```bash
# Verify setup
ls data/nineteenFeaturesDf.csv

# Set API key
export OPENAI_API_KEY='your-key'

# Run the system
python3 main.py --data data/nineteenFeaturesDf.csv

# Check outputs
ls -la output/
```

## 📝 Alternative Datasets

If the Kaggle link becomes unavailable again:

1. **AWS Documentation Samples**
   - https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-examples.html

2. **Security Research Datasets**
   - https://github.com/splunk/attack_data
   - https://github.com/cmu-sei/CERT-Synthetic-Data

3. **Synthetic Generator** (Included)
   - `synthetic_data_generator.py`
   - Generates realistic CloudTrail logs
   - Includes threat patterns

## 💡 For Assignment Submission

If you used synthetic data:

Add this note to your submission:
```
Note: I used the synthetic data generator included in this solution
for testing. The system is fully functional and ready to process
the real CloudTrail dataset from Kaggle once downloaded.

Dataset URL: https://www.kaggle.com/datasets/nobukim/aws-cloudtrails-dataset-from-flaws-cloud
```

## ✨ Success Criteria

You're ready when:
- ✅ `data/nineteenFeaturesDf.csv` exists
- ✅ File size is reasonable (>10MB)
- ✅ CSV has 19 columns
- ✅ Preview shows CloudTrail data
- ✅ No error when running: `python3 main.py --data data/nineteenFeaturesDf.csv`

---

**Need Help?** See `README.md` or `DATA_SOURCES.md` for more details.

