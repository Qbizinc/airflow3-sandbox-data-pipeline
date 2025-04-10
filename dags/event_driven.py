from __future__ import annotations
import os
import pendulum
from airflow.decorators import task
from airflow.operators.python import PythonOperator
from airflow.models.dag import DAG
from airflow.providers.standard.triggers.file import FileDeleteTrigger
from airflow.sdk import Asset, AssetWatcher, chain

file_path = "/include/test/test1.csv"

trigger = FileDeleteTrigger(filepath=file_path)
asset = Asset("include_test", watchers=[AssetWatcher(name="include_test_watcher", trigger=trigger)])

with DAG(
    dag_id="event_driven_test",
    schedule=[asset],
    catchup=False,
):

    @task
    def test_task():
        print("Hello world")

    chain(test_task())