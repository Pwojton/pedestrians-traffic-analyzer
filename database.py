import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_user = os.environ["DB_USER"]
db_pass = os.environ["DB_PASSWORD"]
db_name = os.environ["DB_DATABASE"]
db_host = os.environ["DB_HOST"]
db_port = os.environ["DB_PORT"]


def push_counted_pedestrians(count, time):
    conn = psycopg2.connect(user=db_user, password=db_pass, database=db_name, host=db_host,
                            port=db_port)
    cur = conn.cursor()
    cur.execute(f"INSERT INTO pedestrians_count (ped_count, time) VALUES ('{count}', '{time}')")
    conn.commit()


def push_pedestrians_coming_up_or_down(start_time, end_time, coming_up, coming_down):
    conn = psycopg2.connect(user=db_user, password=db_pass, database=db_name, host=db_host,
                            port=db_port)
    cur = conn.cursor()
    cur.execute(
        f"INSERT INTO pedestrians_coming_up_or_down (start_time, stop_time, ped_count_up, ped_count_down) VALUES ('{start_time}', '{end_time}', '{coming_up}', '{coming_down}')")
    conn.commit()
