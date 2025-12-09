import json
import requests as req


def get_clinical_trials(molecule_name):
    url = "https://clinicaltrials.gov/api/v2/studies"
    params = {
        "query.term": molecule_name,
        "filter.overallStatus": "RECRUITING",
        "pageSize": 3
    }
    try:
        response = req.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            studies = data.get("studies", [])
            titles = [s['protocolSection']['identificationModule']['officialTitle'] for s in studies]
            return json.dumps(titles)
        return "No active trials found"
    except req.exceptions.RequestException as e:
        return {"error fetching trials": str(e)}