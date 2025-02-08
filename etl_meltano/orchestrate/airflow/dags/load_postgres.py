from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def get_execution_date(**context):
    return context['execution_date'].strftime("%Y-%m-%d")

with DAG(
    'load_postgres',
    default_args=default_args,
    schedule_interval='@daily',
    start_date=datetime(2023, 1, 1),
    catchup=False,
    max_active_runs=1,
) as dag:

    get_date = PythonOperator(
        task_id='get_date',
        python_callable=get_execution_date,
        provide_context=True,
    )

    load_parquet_to_postgres = BashOperator(
        task_id='load_parquet_to_postgres',
        bash_command='export EXECUTION_DATE={{ task_instance.xcom_pull(task_ids="get_date") }} && cd /project && meltano run tap-csv target-parquet',
    )

    transform_data = BashOperator(
        task_id='transform_data',
        bash_command='export EXECUTION_DATE={{ task_instance.xcom_pull(task_ids="get_date") }} && cd /project && meltano run tap-csv target-parquet',
    )

    dbt_run = BashOperator(
        task_id='dbt_run_transformations',
        bash_command='dbt run --profiles-dir ../dbt_profiles',
    )

    get_date >> load_parquet_to_postgres >> transform_data >> dbt_run
