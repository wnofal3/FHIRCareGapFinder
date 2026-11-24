from care_gaps.fhir_client import FhirClient

class FakeResponse:
    def __init__(self, data):
        self.data = data

    def json(self):
        return self.data

    def raise_for_status(self):
        pass  # Simulate a successful response (status code 200)

class FakeSession:
    def __init__(self, bundles):
        self.bundles = list(bundles)
        self.calls = []
        self.headers = {}

    def get(self, url, params=None, timeout=None):
        self.calls.append((url, params, timeout))
        return FakeResponse(self.bundles.pop(0) if self.bundles else {"entry": []})

def make_client(bundles):
    client = FhirClient(base_url="http://fake/fhir")
    client.session = FakeSession(bundles)
    return client

def a1c_observation(patient_id, date, value=None):
    obs = {
        "resourceType": "Observation",
        "subject": {"reference": f"Patient/{patient_id}"},
        "effectiveDateTime": date,
    }
    
    if value is not None:
        obs["valueQuantity"] = {"value": value, "unit": "%"}
    
    return {"resource": obs}

def test_search_follows_next_link():
    page1 = {
        "entry": [a1c_observation("1", "2025-01-01", 6.5)],
        "link": [{"relation": "next", "url": "http://fake/fhir?page=2"}],
    }
    page2 = {"entry": [a1c_observation("2", "2025-02-01", 7.0)], "link": []}
    client = make_client([page1, page2])

    results = client.get_a1c_results()

    assert len(client.session.calls) == 2
    assert client.session.calls[1][0] == "http://fake/fhir?page=2"
    assert [r["patient_id"] for r in results] == ["1", "2"]
    

def test_get_a1c_results_parses_observation():
    bundle = {"entry": [a1c_observation("123", "2025-06-01T10:00:00Z", 6.8)], "link": []}
    client = make_client([bundle])
    
    results = client.get_a1c_results()
    assert results == [{
        "patient_id": "123",
        "date": "2025-06-01T10:00:00Z",
        "value": 6.8,
        "unit": "%",
    }]

def test_get_a1c_results_handles_missing_value():
    bundle = {"entry": [a1c_observation("123", "2025-06-01")], "link": []}
    client = make_client([bundle])

    results = client.get_a1c_results()
    assert results == [{
        "patient_id": "123",
        "date": "2025-06-01",
        "value": None,
        "unit": None,
    }]
