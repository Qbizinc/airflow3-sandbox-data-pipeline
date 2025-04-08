# Use the same base image defined in your .env file
FROM ${AIRFLOW_IMAGE_NAME:-apache/airflow:3.0.0.rc1.post4-python3.12}

# Example of installing OS-level dependencies if needed (uncomment/modify)
# USER root
# RUN apt-get update && apt-get install -y --no-install-recommends \
#       some-package \
#    && apt-get clean && rm -rf /var/lib/apt/lists/*
# USER airflow

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python packages
# Using --user might be necessary if running as non-root and encountering permission issues,
# but ensure the installed packages are on the PATH. Often just installing works fine.
RUN pip install --no-cache-dir -r requirements.txt

# Optional: Switch back to airflow user if you switched to root
# USER airflow