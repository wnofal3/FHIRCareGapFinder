from datetime import datetime

CARE_GAP_SQL = """
    SELECT p.patient_id, MAX(a.date) AS last_a1c
    FROM diabetic_patients p
    LEFT JOIN a1c_results a ON p.patient_id = a.patient_id
    GROUP BY p.patient_id
    HAVING MAX(a.date) IS NULL
        OR MAX(a.date) < %(as_of)s - INTERVAL '6 months'
    ORDER BY last_a1c NULLS FIRST
"""

def get_reference_date(conn) -> datetime:
    # get the most recent A1C result date from the database
    with conn.cursor() as cur:
        cur.execute("SELECT MAX(date) FROM a1c_results")
        result = cur.fetchone()
    return result[0] if result and result[0] else None

def find_care_gaps(conn, as_of: datetime | None = None) -> list[dict]:
    # find diabetic patients with no A1C results in the last 6 months
    if as_of is None:
        as_of = get_reference_date(conn)

    with conn.cursor() as cur:
        cur.execute(CARE_GAP_SQL, {"as_of": as_of})
        rows = cur.fetchall()
    return [{"patient_id": row[0], "last_a1c": row[1]} for row in rows]
