from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from datetime import datetime

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

    extract_postgres = DockerOperator(
        task_id='extract_postgres',
        image='meu-meltano',  # Nome da imagem que você criou
        command='meltano run tap-postgres target-parquet',
        docker_url='unix://var/run/docker.sock',
        network_mode='host',  # Ajuste conforme necessário
        volumes=['./project/data/local_data/postgres:/project/data/local_data/'],
        auto_remove=True,
    )

    move_postgres_files = BashOperator(
        task_id='move_postgres_files',
        bash_command=f'mkdir -p ./project/data/local_data/postgres/{{{{ ds_nodash }}}}; mv ./project/data/local_data/postgres/* ./project/data/local_data/postgres/{{{{ ds_nodash }}}}/',
    )

    extract_csv = DockerOperator(
        task_id='extract_csv',
        image='meu-meltano',  # Nome da imagem que você criou
        command='meltano run tap-csv target-parquet',
        docker_url='unix://var/run/docker.sock',
        network_mode='host',  # Ajuste conforme necessário
        volumes=['./project/data/local_data/csv:/project/data/local_data/'],
        auto_remove=True,
    )

    move_csv_files = BashOperator(
        task_id='move_csv_files',
        bash_command=f'mkdir -p ./project/data/local_data/csv/{{{{ ds_nodash }}}}; mv ./project/data/local_data/csv/* ./project/data/local_data/csv/{{{{ ds_nodash }}}}/',
    )

    extract_postgres >> extract_csv
