# airflow3-sandbox-data-pipeline
This repository is for testing and running the sandbox data pipeline in airflow 3

If installing on an EC2 instance use setup_ec2.sh to launch instance

To start airflow 3.

```commandline
cd airflow3-sandbox-data-pipeline
```

Add .env file the values for each key. You can generate the keys like: 

```commandline
# For Fernet Key
python3 -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'

# Run this 3 times for the 3 different Secret Keys (Webserver, Internal API, JWT)
python3 -c 'import secrets; print(secrets.token_hex(32))'
```

Then run.

```commandline
sudo docker compose build --no-cache
sudo docker compose up airflow-init
sudo docker compose up -d
```

IMPORTANT: When launching an EC2 instance you might have to change the lines to an elastic/public URL

```yaml
AIRFLOW__WEBSERVER__BASE_URL: http://airflow-api-server:8080
AIRFLOW__CORE__EXECUTION_API_SERVER_URL: http://airflow-api-server:8080/execution/
```