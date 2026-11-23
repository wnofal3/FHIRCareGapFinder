from care_gaps.fhir_client import FhirClient
from care_gaps import db

def main():
    client = FhirClient()
    patient_ids = client.get_diabetic_patient_ids()
    a1c_results = client.get_a1c_results()

    with db.get_connection() as conn:
        db.create_tables(conn)
        db.save_patients(conn, patient_ids)
        db.save_a1c_results(conn, a1c_results)

    print(f"Saved {len(patient_ids)} diabetic patients and {len(a1c_results)} A1C results to the database.")

if __name__ == "__main__":
    main()