from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime
import os

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
}

def get_data_interval_start(**context):
    return context['data_interval_start'].strftime("%Y-%m-%d").strip()

with DAG(
    'extract_local',
    default_args=default_args,
    schedule_interval='@daily',
    start_date=datetime(2023, 1, 1),
    catchup=False,
) as dag:

    get_date = PythonOperator(
    task_id='get_date',
    python_callable=get_data_interval_start,
    provide_context=True,
    dag=dag
    )

    extract_csv = BashOperator(
        task_id='extract_csv_to_parquet',
        bash_command='export EXECUTION_DATE={{ task_instance.xcom_pull(task_ids="get_date") }} &&'
                     'cd /project && '
                     'meltano el tap-csv target-parquet',
    )

    extract_postgres = BashOperator(
        task_id='extract_postgres_to_parquet',
        bash_command='export EXECUTION_DATE={{ task_instance.xcom_pull(task_ids="get_date") }} &&'
                     'cd /project && '
                     'meltano el tap-postgres target-parquet',
    )

    get_date >> extract_csv >> extract_postgres