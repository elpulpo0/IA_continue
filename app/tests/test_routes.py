from fastapi.testclient import TestClient
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_generate():
    response = client.post("/generate")
    assert response.status_code == 200

def test_retrain():
    client.post("/generate")
    response = client.post("/retrain")
    assert response.status_code == 200

def test_predict():
    client.post("/generate")
    client.post("/retrain")
    response = client.get("/predict")
    print("RESPONSE TEXT:", response.text)
    assert response.status_code == 200

def test_predict_no_model():
    response = client.get("/predict")
    if response.status_code == 500:
        assert "error" in response.json()
