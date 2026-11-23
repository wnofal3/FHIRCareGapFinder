import csv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CSV_PATH = PROJECT_ROOT / "sample_output" / "care_gaps.csv"
FIELDNAMES = ["patient_id", "last_a1c"]

def write_care_gaps_csv(gaps: list[dict], path: Path = DEFAULT_CSV_PATH) -> Path:
    # 1. note whether path.exists() | "Created" vs "Overwrote"
    print(f"Creating CSV file at {path}" if not path.exists() else f"Overwriting CSV file at {path}")
    # 2. open(path, "w", newline="")
    path.parent.mkdir(parents=True, exist_ok=True)  # Ensure the directory exists
    with open(path, "w", newline="") as file:
        # 3. csv.DictWriter(f, fieldnames=FIELDNAMES), then writeheader()
        csv_writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        csv_writer.writeheader()
        # 4. for each gap: write a row; turn last_a1c into a date string, or "never" if None
        for gap in gaps:
            last_a1c = gap["last_a1c"].date().isoformat() if gap["last_a1c"] else "never"
            csv_writer.writerow({"patient_id": gap["patient_id"], "last_a1c": last_a1c})
    
    # 5. print the action and path, return path
    print(f"CSV file written to {path}")
    return path