from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.operators.bash import BashOperator
from datetime import datetime
from docker.types import Mount

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
}

with DAG(
    'extract_to_local',
    default_args=default_args,
    description='Extrai os dados do postgres e do csv para pasta local',
    schedule_interval='@daily',
    start_date=datetime(2025, 3, 1),
    catchup=False,
) as dag:

    create_postgres_dir = BashOperator(
        task_id='create_postgres_dir',
        bash_command=f'mkdir -p ./project/data/local_data/postgres'
    )

    extract_postgres = DockerOperator(
        task_id='extract_postgres',
        image='meu-meltano',
        command='meltano run tap-postgres target-parquet',
        docker_url='unix://var/run/docker.sock',
        network_mode='host',
        mounts=[
            Mount(
                source='./etl_project/data/local_data/',
                target='/project/data/local_data/',
                type='volume'
            )
        ],
        auto_remove=True,
    )

    move_postgres_files = BashOperator(
        task_id='move_postgres_files',
        bash_command=f'mv ./project/data/local_data/extract/* ./project/data/local_data/postgres/',
    )

    create_csv_dir = BashOperator(
        task_id='create_csv_dir',
        bash_command=f'mkdir -p ./project/data/local_data/csv',
    )

    extract_csv = DockerOperator(
        task_id='extract_csv',
        image='meu-meltano',
        command='meltano run tap-csv target-parquet',
        docker_url='unix://var/run/docker.sock',
        network_mode='host',
        mounts=[
            Mount(
                source='./project/data/local_data/',
                target='/project/data/local_data/',
                type='volume'
            )
        ],
        auto_remove=True,
    )

    move_csv_files = BashOperator(
        task_id='move_csv_files',
        bash_command=f'mv ./project/data/local_data/extract/* ./project/data/local_data/csv/',
    )

    create_postgres_dir >> extract_postgres >> move_postgres_files
    extract_postgres >> create_csv_dir >> extract_csv >> move_csv_files
