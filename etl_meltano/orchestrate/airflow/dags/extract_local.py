from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

logger = logging.getLogger(__name__)

DEFAULT_ARGS = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "catchup": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "concurrency": 1,
}

PROJECT_ROOT = os.getenv("MELTANO_PROJECT_ROOT", os.getcwd())
MELTANO_BIN = ".meltano/run/bin"

if not os.path.exists(os.path.join(PROJECT_ROOT, MELTANO_BIN)):
    logger.warning(
        "A symlink to the 'meltano' executable could not be found at '%s'. "
        "Falling back on expecting it to be in the PATH instead. ",
        MELTANO_BIN,
    )
    MELTANO_BIN = "meltano"

# Função para criar o caminho da pasta com a data de execução
def get_date_path(**kwargs):
    execution_date = kwargs["execution_date"]
    date_str = execution_date.strftime("%Y-%m-%d")
    return date_str

# DAG para mover dados do CSV e do PostgreSQL para pastas com a data de execução
with DAG(
    "meltano_move_data",
    default_args=DEFAULT_ARGS,
    schedule_interval="@daily",
    start_date=datetime(2023, 1, 1),
    catchup=False,
) as dag:
    # Tarefa para extrair dados do CSV para Parquet
    extract_csv = BashOperator(
        task_id="extract_csv_to_parquet",
        bash_command=f"cd {PROJECT_ROOT}; {MELTANO_BIN} run tap-csv target-parquet",
    )

    # Tarefa para mover dados do CSV para pasta com a data de execução
    move_csv = BashOperator(
        task_id="move_csv_to_date_folder",
        bash_command=f"""
            date_path=$(date +'%Y-%m-%d')
            mkdir -p /project/data/local_data/csv/$date_path
            mv /project/data/local_data/extract/* /project/data/local_data/csv/$date_path/
        """,
    )

    # Tarefa para extrair dados do PostgreSQL para Parquet
    extract_postgres = BashOperator(
        task_id="extract_postgres_to_parquet",
        bash_command=f"cd {PROJECT_ROOT}; {MELTANO_BIN} run tap-postgres target-parquet",
    )

    # Tarefa para mover dados do PostgreSQL para pasta com a data de execução
    move_postgres = BashOperator(
        task_id="move_postgres_to_date_folder",
        bash_command=f"""
            date_path=$(date +'%Y-%m-%d')
            mkdir -p /project/data/local_data/postgres/$date_path
            mv /project/data/local_data/extract/* /project/data/local_data/postgres/$date_path/
        """,
    )

    # Definindo a ordem das tarefas
    extract_csv >> move_csv
    extract_postgres >> move_postgres
