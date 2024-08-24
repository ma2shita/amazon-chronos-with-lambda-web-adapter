from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_readness_check_from_lambda_web_adapter():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "OK"}

def test_forecast1_json():
    response = client.post("/forecast.json", json={"historical": [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29]})
    assert response.status_code == 200
    json = response.json()
    #=> {"forecast":{"min":[29.978005599975585],"median":[30.02199363708496],"max":[30.285923767089844]}}
    low, high = 29, 31
    fc = json["forecast"]
    assert len(fc["min"]) == 1    and (low < fc["min"][0] < high)
    assert len(fc["median"]) == 1 and (low < fc["median"][0] < high)
    assert len(fc["max"]) == 1    and (low < fc["max"][0] < high)

def test_forecast5_json():
    response = client.post("/forecast.json", json={"historical": [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29]}, params={"prediction_length": 5})
    assert response.status_code == 200
    json = response.json()
    assert len(json["forecast"]["min"]) == 5
    assert isinstance(json["forecast"]["min"][-1], (float, int))

import io
def test_forecast_png():
    response = client.post("/forecast.png", json={"historical": [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29]})
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert io.BytesIO(response.content).read(4) == b"\x89PNG"
