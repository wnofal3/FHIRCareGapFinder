import os
import psycopg
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file
DATABASE_URL = os.environ["DATABASE_URL"]


def get_connection():
    # return psycopg.connect(DATABASE_URL)
    return psycopg.connect(DATABASE_URL)


def create_tables(conn):
    # CREATE TABLE IF NOT EXISTS diabetic_patients (patient_id TEXT PRIMARY KEY)
    conn.execute("""
            CREATE TABLE IF NOT EXISTS diabetic_patients (
                patient_id TEXT PRIMARY KEY
            )
        """)
    # CREATE TABLE IF NOT EXISTS a1c_results (
    #     id SERIAL PRIMARY KEY, patient_id TEXT, date TIMESTAMPTZ,
    #     value NUMERIC, unit TEXT)
    conn.execute("""
            CREATE TABLE IF NOT EXISTS a1c_results (
                id SERIAL PRIMARY KEY,
                patient_id TEXT,
                date TIMESTAMPTZ,
                value NUMERIC,
                unit TEXT
            )
        """)
    # run each with conn.execute(...), then conn.commit()
    conn.commit()


def save_patients(conn, patient_ids: set[str]):
    # clear the table first (DELETE FROM ...) so reruns don't duplicate rows
    # insert each id: INSERT INTO diabetic_patients (patient_id) VALUES (%s)
    rows = [(pid,) for pid in patient_ids]

    with conn.cursor() as cur:
        cur.execute("DELETE FROM diabetic_patients")
        cur.executemany("INSERT INTO diabetic_patients (patient_id) VALUES (%s)", rows)

    conn.commit()


def save_a1c_results(conn, results: list[dict]):
    # clear the table, then insert each row
    # VALUES (%(patient_id)s, %(date)s, %(value)s, %(unit)s)
    with conn.cursor() as cur:
        cur.execute("DELETE FROM a1c_results")
        cur.executemany(
            "INSERT INTO a1c_results (patient_id, date, value, unit) VALUES (%(patient_id)s, %(date)s, %(value)s, %(unit)s)",
            results
        )

    conn.commit()