from datetime import datetime, timedelta
import os
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators import (S3ToRedshiftOperator, LoadFactOperator,
                               LoadDimensionOperator, DataQualityOperator)
from helpers import SqlQueries

# KEY = os.environ.get('AWS_KEY')
# AWS_SECRET = os.environ.get('AWS_SECRET')

default_args = {
    'owner': 'udacity',
    'start_date': datetime(2019, 1, 12),
    'depends_on_past': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'catchup': False,
    'email_on_retry': False
}

dag = DAG('final_dag',
          default_args=default_args,
          start_date=datetime(2018, 11, 1),
          description='Load and transform data in Redshift with Airflow',
          schedule_interval='0 * * * *'
          )

start_operator = DummyOperator(task_id='Begin_execution', dag=dag)

stage_events_to_redshift = S3ToRedshiftOperator(
    task_id='Stage_events',
    dag=dag,
    aws_credentials_id='aws_credentials',
    redshift_conn_id="redshift",
    table="staging_events",
    s3_bucket="udacity-dend",
    s3_key="log_data",
)

stage_songs_to_redshift = S3ToRedshiftOperator(
    task_id='Stage_songs',
    dag=dag,
    aws_credentials_id='aws_credentials',
    redshift_conn_id="redshift",
    table="staging_songs",
    s3_bucket="udacity-dend",
    s3_key="song_data",
)

load_songplays_table = LoadFactOperator(
    task_id='Load_songplays_fact_table',
    dag=dag,
    redshift_conn_id="redshift"
)

load_user_dimension_table = LoadDimensionOperator(
    task_id='Load_user_dim_table',
    dag=dag,
    redshift_conn_id="redshift",
    table='users'
)

load_song_dimension_table = LoadDimensionOperator(
    task_id='Load_song_dim_table',
    dag=dag,
    redshift_conn_id="redshift",
    table='songs',
)

load_artist_dimension_table = LoadDimensionOperator(
    task_id='Load_artist_dim_table',
    dag=dag,
    redshift_conn_id="redshift",
    table='artists',

)

load_time_dimension_table = LoadDimensionOperator(
    task_id='Load_time_dim_table',
    dag=dag,
    redshift_conn_id="redshift",
    table='time',
)

run_quality_checks = DataQualityOperator(
    task_id='Run_data_quality_checks',
    dag=dag,
    redshift_conn_id="redshift",
    table='songs',
)

end_operator = DummyOperator(task_id='Stop_execution', dag=dag)

start_operator >> stage_events_to_redshift
start_operator >> stage_songs_to_redshift
stage_events_to_redshift >> load_songplays_table
stage_songs_to_redshift >> load_songplays_table
load_songplays_table >> load_user_dimension_table
load_songplays_table >> load_song_dimension_table
load_songplays_table >> load_artist_dimension_table
load_songplays_table >> load_time_dimension_table
load_user_dimension_table >> run_quality_checks
load_song_dimension_table >> run_quality_checks
load_artist_dimension_table >> run_quality_checks
load_time_dimension_table >> run_quality_checks
run_quality_checks >> end_operator
