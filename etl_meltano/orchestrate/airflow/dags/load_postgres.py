from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os

default_args = {
    'owner': 'data_engineer',
    'depends_on_past': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=10),
    'email_on_failure': True,
}

def find_latest_parquet(directory_base: str, **kwargs) -> str:
    data_interval_start = kwargs['data_interval_start'].strftime("%Y-%m-%d")

    if "postgres" in directory_base:
        directory = os.path.join(directory_base, data_interval_start, "public-orders")
    else:
        directory = os.path.join(directory_base, data_interval_start, "order_details")

    if not os.path.exists(directory):
        raise FileNotFoundError(f"Diretório não encontrado: {directory}")

    parquet_files = [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f.endswith(".parquet") and os.path.isfile(os.path.join(directory, f))
    ]

    if not parquet_files:
        raise FileNotFoundError(f"Nenhum arquivo Parquet encontrado em: {directory}")

    latest_file = max(parquet_files, key=os.path.getmtime)

    return latest_file

with DAG(
    'load_postgres',
    default_args=default_args,
    description='DAG para processamento de arquivos Parquet com caminhos dinâmicos',
    schedule_interval='@daily',
    start_date=datetime(2023, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=['parquet', 'meltano'],
) as dag:

    localizar_csv = PythonOperator(
        task_id='localizar_arquivo_csv',
        python_callable=find_latest_parquet,
        op_kwargs={'directory_base': '/project/data/tap-csv'},
        provide_context=True,
    )

    carregar_csv = BashOperator(
        task_id='carregar_csv_postgres',
        bash_command='export TAP_PARQUET_FILEPATH={{ task_instance.xcom_pull(task_ids="localizar_arquivo_csv") }} && '
                     'cd /project && '
                     'meltano run tap-parquet target-postgres',
    )

    localizar_postgres = PythonOperator(
        task_id='localizar_arquivo_postgres',
        python_callable=find_latest_parquet,
        op_kwargs={'directory_base': '/project/data/tap-postgres'},
        provide_context=True,
    )

    carregar_postgres = BashOperator(
        task_id='carregar_postgres_destino',
        bash_command='export TAP_PARQUET_FILEPATH={{ task_instance.xcom_pull(task_ids="localizar_arquivo_postgres") }} && '
                     'cd /project && '
                     'meltano run tap-parquet target-postgres',
    )

    transformar_dados = BashOperator(
        task_id='executar_transformacoes_dbt',
        bash_command='cd /project && '
                     'meltano invoke dbt-postgres:run --profiles-dir=/project/dbt_profiles',
    )

    localizar_csv >> carregar_csv >> localizar_postgres >> carregar_postgres >> transformar_dados
