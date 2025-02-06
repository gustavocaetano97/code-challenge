from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
}

with DAG(
    'meltano_move_data',
    default_args=default_args,
    schedule_interval='@daily',
    start_date=datetime(2025, 3, 1),
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
        for stream_dir in /project/data/local_data/extract/*; do
            if [ -d "$stream_dir" ]; then
                mv "$stream_dir" /project/data/local_data/csv/$date_path/
            fi
        done
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
        mkdir -p /project/data/local_data/csv/$date_path
        for stream_dir in /project/data/local_data/extract/*; do
            if [ -d "$stream_dir" ]; then
                mv order_details /project/data/local_data/csv/$date_path/
            fi
        done
    """,
    )

    extract_csv >> move_csv
    extract_postgres >> move_postgres
