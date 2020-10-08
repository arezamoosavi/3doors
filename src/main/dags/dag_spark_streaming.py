from __future__ import print_function
from datetime import datetime

import airflow
from airflow.operators.bash_operator import BashOperator


args = {
    "owner": "3doors",
    "start_date": datetime(year=2020, month=9, day=10, hour=1, minute=0, second=0),
    "provide_context": True,
}

dag = airflow.DAG(
    dag_id="spark_atm_streaming",
    default_args=args,
    schedule_interval="@once",
    max_active_runs=1,
)

create_spark_streaming_kafka = BashOperator(
    task_id="etl_streaming_data",
    bash_command="spark-submit "
    "--packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.7,org.apache.kafka:kafka-clients:2.3.0 "
    "--jars {{var.value.airflow_home}}/postgresql-9.4.1207.jre6.jar "
    "--master spark://spark:7077 "
    "--num-executors 1 --driver-memory 1g --executor-memory 1g --executor-cores 1 "
    "{{var.value.airflow_home}}/dags/etl/stream_data_posgres.py ",
    dag=dag,
)

create_spark_streaming_kafka
