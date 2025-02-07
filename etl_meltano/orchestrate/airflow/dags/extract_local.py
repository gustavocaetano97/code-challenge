from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
}

with DAG(
    'extract_to_local',
    default_args=default_args,
    schedule_interval='@daily',
    start_date=datetime(2023, 1, 1),
    catchup=False,
) as dag:
    extract_csv = BashOperator(
        task_id='extract_csv_to_parquet',
        bash_command='cd /path/to/meltano/project; meltano run tap-csv target-parquet',
    )

    move_csv = BashOperator(
        task_id='move_csv_to_date_folder',
        bash_command="""
            date_path=$(date +'%Y-%m-%d')
            mkdir -p /project/data/local_data/csv/$date_path
            mv /project/data/local_data/extract/* /project/data/local_data/csv/$date_path/
        """,
    )

    extract_postgres = BashOperator(
        task_id='extract_postgres_to_parquet',
        bash_command='cd /path/to/meltano/project; meltano run tap-postgres target-parquet',
    )

    move_postgres = BashOperator(
        task_id='move_postgres_to_date_folder',
        bash_command="""
            date_path=$(date +'%Y-%m-%d')
            mkdir -p /project/data/local_data/postgres/$date_path
            mv /project/data/local_data/extract/* /project/data/local_data/postgres/$date_path/
        """,
    )

    extract_csv >> move_csv
    extract_postgres >> move_postgres
