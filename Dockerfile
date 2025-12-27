# Multi-stage Docker build for AI Threat Hunting System

FROM python:3.11-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY query_generator.py .
COPY evaluator.py .
COPY main.py .
COPY utils.py .

# Create directories
RUN mkdir -p /app/data /app/output

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Default command
CMD ["python", "main.py", "--help"]

# -----------------------------------
# Production stage
# -----------------------------------
FROM base as production

# Run as non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import sys; sys.exit(0)"

# -----------------------------------
# Development stage with Jupyter
# -----------------------------------
FROM base as development

# Install additional dev dependencies
RUN pip install --no-cache-dir \
    jupyter \
    notebook \
    jupyterlab \
    ipywidgets \
    streamlit

# Copy additional files
COPY demo.ipynb .

# Expose ports for Jupyter and Streamlit
EXPOSE 8888 8501

# Default to Jupyter Lab
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--allow-root", "--no-browser"]

