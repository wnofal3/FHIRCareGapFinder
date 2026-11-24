import json
import os
from pathlib import Path
import requests
from dotenv import load_dotenv

# parent script directory -> working directory
SCRIPT_DIR = Path(__file__).resolve().parents[2]

load_dotenv()

BASE_URL = os.environ["FHIR_BASE_URL"]
DATA_DIR = SCRIPT_DIR / Path("data/synthea_sample_data_fhir_latest")
HEADERS = {"Content-Type": "application/fhir+json"}

def post_bundle(path: Path) -> bool:
    bundle = json.loads(path.read_text(encoding="utf-8"))

    try:
        response = requests.post(BASE_URL, json=bundle, headers=HEADERS, timeout=60)

        if not 200 <= response.status_code < 300:
            print(f"[FAIL] {path.name} ({response.status_code}): {response.text[:150]}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        print(f"File path: {path.name}")
        return False

    return True # handled false cases in try/except block

def main():
    files = sorted(DATA_DIR.glob("*.json"))
    print(f"Found {len(files)} files in {DATA_DIR}")
    hospital_list, practitioner_list, patient_list = [], [], [] # separate lists based on file name

    # iterate through files to group based on name prefix
    for file in files:
        if file.name.startswith("hospitalInformation"):
            hospital_list.append(file)
        elif file.name.startswith("practitionerInformation"):
            practitioner_list.append(file)
        else:
            patient_list.append(file)
    
    files_tuple = [("hospitals", hospital_list), ("practitioners", practitioner_list), ("patients", patient_list)]

    # process each bundle one file at a time
    for group_name, group_files in files_tuple:
        passed, failed = 0, 0
        for file in group_files:
            processing_result = post_bundle(file)

            if processing_result:
                passed += 1
            else:
                failed += 1

        print(f"Bundle ({group_name}): {passed} / {len(group_files)} | {failed} Failed.")

if __name__ == "__main__":
    main()