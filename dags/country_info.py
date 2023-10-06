from airflow import DAG
from airflow.decorators import task
from datetime import datetime, timedelta
import requests
from airflow.hooks.postgres_hook import PostgresHook
import logging


def get_Redshift_connection(autocommit=True):
    hook = PostgresHook(postgres_conn_id='redshift_dev_db')
    conn = hook.get_conn()
    conn.autocommit = autocommit
    return conn.cursor()


@task
def get_country_info():
    url = 'https://restcountries.com/v3/all'
    response = requests.get(url)
    data = response.json()
    countries = []

    for country_info in data:
        country = country_info['name']['official']
        population = country_info['population']
        area = country_info['area']

        """
        나라 이름중에서 INFO - syntax error at or near "s"LINE 1: ...Macao Special Administrative Region of the People's Republic...
        이런 오류가 계속 떠서 load에 실패 했다.
        아마도 sql 쿼리에서 문자열에 작은 따옴표 를 사용하고 있는데,
        문자열 안에 있는 작은 따옴표를 이스케이프 하지 않아서 sql 쿼리가 제대로 파싱되지 않은것 같다.
        """
        country = country.replace("'", "''")
        countries.append([country, population, area])

    return countries


@task
def load(schema, table, countries):
    logging.info("Load started")
    cur = get_Redshift_connection()
    try:
        cur.execute("BEGIN;")
        cur.execute(f"DROP TABLE IF EXISTS {schema}.{table};")
        cur.execute(f"""
            CREATE TABLE {schema}.{table} (
                country VARCHAR(255),
                population INT,
                area FLOAT
            );""")
        for c in countries:
            sql = f"INSERT INTO {schema}.{table} VALUES ('{c[0]}', {c[1]}, {c[2]});"
            cur.execute(sql)
        cur.execute("COMMIT;")
        logging.info("Load done")
    # except Exception as error:
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
        cur.execute("ROLLBACK;")
        raise

    logging.info("load done")


with DAG(
    dag_id='country_info',
    start_date=datetime(2023, 5, 30),
    catchup=False,
    tags=['API'],
    schedule='30 6 * * 6'
) as dag:

    results = get_country_info()
    load("jaewoo98y", "country_info", results)
