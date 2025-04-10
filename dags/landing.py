# dags/s3_sensor_mover_producer_dag.py
from __future__ import annotations

import pendulum
import logging
import os

from airflow.decorators import dag, task
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from airflow.sdk.definitions.asset import Asset

S3_BUCKET_NAME = "qbiz-dev-training"  # IMPORTANT: Replace with your bucket name
LANDING_PREFIX = "airflow3/landing/"        # IMPORTANT: Source prefix (needs trailing '/')
READY_PREFIX = "airflow3/ready/"            # IMPORTANT: Destination prefix (needs trailing '/')
FILE_PATTERN = "new_file_*.csv"    # IMPORTANT: File pattern to look for in landing area
AWS_CONN_ID = "aws"        # IMPORTANT: Your AWS Connection ID in Airflow

s3_ready_dataset = Asset(f"s3://{S3_BUCKET_NAME}/{READY_PREFIX}")

log = logging.getLogger(__name__)

@task(task_id="move_file_to_ready", outlets=[s3_ready_dataset])
def move_file_and_update_dataset(source_key: str, source_bucket: str, dest_prefix: str, aws_conn_id: str):
    """
    Moves a specific file from source to destination prefix in S3 and updates dataset.

    :param source_key: The full S3 key of the file found by the sensor (e.g., 'landing/file.csv').
    :param source_bucket: The S3 bucket name.
    :param dest_prefix: The destination prefix (e.g., 'ready/'). Ensure it ends with '/'.
    :param aws_conn_id: The Airflow connection ID for AWS.
    """
    if not source_key:
        log.error("No source key provided to move.")
        raise ValueError("Source key cannot be empty.")

    hook = S3Hook(aws_conn_id=aws_conn_id)
    file_name = os.path.basename(source_key)
    destination_key = os.path.join(dest_prefix, file_name).replace("\\", "/") # Ensure forward slashes

    log.info(f"Moving s3://{source_bucket}/{source_key} to s3://{source_bucket}/{destination_key}")

    try:
        # S3 move is copy + delete
        hook.copy_object(
            source_bucket_key=source_key,
            dest_bucket_key=destination_key,
            source_bucket_name=source_bucket,
            dest_bucket_name=source_bucket,
        )
        log.info(f"Successfully copied to {destination_key}")

        hook.delete_objects(bucket=source_bucket, keys=[source_key])
        log.info(f"Successfully deleted source {source_key}")

        # The task success + outlets parameter handles the Dataset update
        log.info(f"Task successful, dataset {s3_ready_dataset.uri} will be updated.")

    except Exception as e:
        log.error(f"Error during S3 move operation: {e}")
        raise

@dag(
    dag_id="s3_sensor_mover_producer_taskflow",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="*/5 * * * *",
    catchup=False,
    tags=["s3", "sensor", "dataset", "producer", "taskflow"],
    doc_md=f"""
    ### S3 Sensor and Mover DAG (Producer - TaskFlow)

    Uses S3KeySensor and @task to move files from landing to ready and update Dataset.
    Checks for `{FILE_PATTERN}` in `s3://{S3_BUCKET_NAME}/{LANDING_PREFIX}`.
    Moves file to `s3://{S3_BUCKET_NAME}/{READY_PREFIX}`.
    Updates Dataset: `{s3_ready_dataset.uri}`.
    """,
)
def s3_sensor_mover_producer_taskflow():
    # Task 1: Sensor remains a standard operator instantiation
    sense_landing_file = S3KeySensor(
        task_id="sense_landing_file",
        bucket_name=S3_BUCKET_NAME,
        bucket_key=f"{LANDING_PREFIX}{FILE_PATTERN}",
        wildcard_match=True,
        aws_conn_id=AWS_CONN_ID,
        mode="reschedule",
        poke_interval=60,
        timeout=60 * 30,
    )

    move_task = move_file_and_update_dataset(
        source_key=sense_landing_file.output, # Pass XCom result using .output
        source_bucket=S3_BUCKET_NAME,
        dest_prefix=READY_PREFIX,
        aws_conn_id=AWS_CONN_ID,
    )

s3_sensor_mover_producer_taskflow()