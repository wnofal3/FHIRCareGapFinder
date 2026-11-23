from care_gaps.fhir_client import FhirClient
from care_gaps import db
from care_gaps import care_gaps
from care_gaps import export

def main():
    client = FhirClient()
    patient_ids = client.get_diabetic_patient_ids()
    a1c_results = client.get_a1c_results()

    with db.get_connection() as conn:
        db.create_tables(conn)
        db.save_patients(conn, patient_ids)
        db.save_a1c_results(conn, a1c_results)

        # identify care gaps
        gaps = care_gaps.find_care_gaps(conn)
        print(f"{len(gaps)} of {len(patient_ids)} diabetic patients have a care gap")
        
        for gap in gaps:
            print(f"Patient {gap["patient_id"]}: Last A1C: {gap["last_a1c"].date() if gap["last_a1c"] else 'None'}")

        # export to CSV
        export.write_care_gaps_csv(gaps)


    print(f"Saved {len(patient_ids)} diabetic patients and {len(a1c_results)} A1C results to the database.")

if __name__ == "__main__":
    main()