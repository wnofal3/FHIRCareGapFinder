import requests
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

BASE_URL = os.environ["FHIR_BASE_URL"]
DIABETES_CODE = "http://snomed.info/sct|44054006"
A1C_CODE = "http://loinc.org|4548-4"


class FhirClient:
    def __init__(self, base_url: str = BASE_URL, timeout: int = 30):
        # store base_url and timeout
        # create a requests.Session and set the Accept header to application/fhir+json
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/fhir+json"
        })


    def _search(self, resource_type: str, params: dict):
        """Yield every resource across all pages of a search."""
        # 1. build the first URL from base_url + resource_type, and send params
        url = f"{self.base_url}/{resource_type}"

        # 2. loop:
                #      GET the URL, raise on bad status, parse the JSON Bundle
                #      for each item in bundle.get("entry", []): yield item["resource"]
                #      find the link whose "relation" is "next"
                #      if none, stop; otherwise set url to its "url" and clear params
                #      (the next link already has the query baked in)
        while url:
            try:
                response = self.session.get(url, params=params, timeout=self.timeout)

                # raise an HTTPError if the status is 4xx or 5xx
                response.raise_for_status()

                bundle = response.json()
                # print(bundle)

            except requests.exceptions.HTTPError as http_err:
                print(f"HTTP error occurred: {http_err} (Status code: {response.status_code})")
                raise
            except requests.exceptions.RequestException as err:
                print(f"Other request error occurred: {err}")
                raise

            # iterate through entries
            for entry in bundle.get("entry", []):
                yield entry["resource"]

            url = None
            for link in bundle.get("link", []):
                if link["relation"] == "next":
                    url = link["url"]
                    params = None

    def get_diabetic_patient_ids(self) -> set[str]:
        # search Condition by DIABETES_CODE
        # pull the patient id out of subject.reference ("Patient/abc" -> "abc")
        patient_ids = set()
        resource_type, params = "Condition", {"code": DIABETES_CODE, "_count": 100}
        
        
        for condition in self._search(resource_type, params):
            patient_reference = condition["subject"]["reference"]
            patient_id = patient_reference.split("/")[-1]
            patient_ids.add(patient_id)

        return patient_ids

    def get_a1c_results(self) -> list[dict]:
        # search Observation by A1C_CODE
        # return [{"patient_id", "date", "value", "unit"}, ...]
        a1c_results = []
        resource_type, params = "Observation", {"code": A1C_CODE, "_count": 100}

        for observation in self._search(resource_type, params):
            patient_reference = observation["subject"]["reference"]
            patient_id = patient_reference.split("/")[-1]
            date = observation.get("effectiveDateTime")
            value_quantity = observation.get("valueQuantity", {})
            value = value_quantity.get("value")
            unit = value_quantity.get("unit")

            a1c_results.append({
                "patient_id": patient_id,
                "date": date,
                "value": value,
                "unit": unit
            })

        return a1c_results


if __name__ == "__main__":
    # quick manual check: print how many diabetic patients and how many A1c results
    client = FhirClient()
    diabetic_patients = client.get_diabetic_patient_ids()
    a1c_results = client.get_a1c_results()

    # test counts for each method
    print(f"Number of diabetic patients: {len(diabetic_patients)}")
    print(f"Number of A1C results: {len(a1c_results)}")
    print(f"Sample A1C results: {a1c_results[:5]}")