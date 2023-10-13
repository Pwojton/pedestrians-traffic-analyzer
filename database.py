import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_user = os.environ["DB_USER"]
db_pass = os.environ["DB_PASSWORD"]
db_name = os.environ["DB_DATABASE"]
db_host = os.environ["DB_HOST"]
db_port = os.environ["DB_PORT"]


def push_count_data(count):
    conn = psycopg2.connect(user=db_user, password=db_pass, database=db_name, host=db_host,
                            port=db_port)
    cur = conn.cursor()
    cur.execute(f"INSERT INTO test (pedestrians_count, fetched_on) VALUES ('{count}', now())")
    conn.commit()
