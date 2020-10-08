import logging
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator

from dags.etl.produce_data import process_data_kafka


logger = logging.getLogger(__name__)
logger.setLevel("WARNING")


args = {
    "owner": "3doors",
    "start_date": datetime(year=2020, month=9, day=10, hour=1, minute=0, second=0),
    "provide_context": True,
}


kafka_dag = DAG(
    dag_id="once_data_to_kafka",
    default_args=args,
    schedule_interval="@once",
    max_active_runs=1,
)


process_data_kafka = PythonOperator(
    task_id="data_to_kafka_producer",
    python_callable=process_data_kafka,
    op_kwargs={
        "path_of_data": "dags/atm_data.csv",
        "broker_address": "kafka:9092",
        "topic_name": "atm_transactions",
    },
    dag=kafka_dag,
)

process_data_kafka
