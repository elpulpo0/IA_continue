import datetime
import pandas as pd
import numpy as np
import mlflow
import mlflow.sklearn
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sklearn.linear_model import LogisticRegression
from database import Dataset, SessionLocal
from config.logger import configure_logger
import os
from config.settings import PROJECT_ROOT

logger = configure_logger()

router = APIRouter()

MLRUNS_DB_PATH = os.path.join(PROJECT_ROOT, "db", "mlruns.db")

db_dir = os.path.dirname(MLRUNS_DB_PATH)
if not os.path.exists(db_dir):
    os.makedirs(db_dir)

mlflow.set_tracking_uri(f"sqlite:///{MLRUNS_DB_PATH}")


def get_last_model_uri():
    client = mlflow.tracking.MlflowClient()
    experiment = client.get_experiment_by_name("Default")
    if not experiment:
        return None
    experiment_id = experiment.experiment_id
    runs = client.search_runs(
        experiment_ids=[experiment_id], order_by=["start_time desc"], max_results=1
    )
    if not runs:
        return None
    run_id = runs[0].info.run_id
    return f"runs:/{run_id}/model"


@router.get("/health")
async def health_check():
    return JSONResponse(status_code=200, content={"status": "ok"})


@router.post("/generate")
def generate_dataset():
    session = SessionLocal()
    np.random.seed()
    now = datetime.datetime.now()
    hour_mod = now.hour % 2

    X1 = np.random.rand(100)
    X2 = np.random.rand(100) - 0.5 if hour_mod == 1 else np.random.rand(100)
    y = ((X1 + X2) > 1).astype(int)

    for f1, f2, t in zip(X1, X2, y):
        entry = Dataset(feature1=f1, feature2=f2, target=int(t))
        session.add(entry)
    session.commit()
    session.close()
    logger.info(f"Dataset generated successfully")
    return {"message": "Dataset generated successfully"}


@router.post("/retrain")
def retrain_model():
    session = SessionLocal()
    data = session.query(Dataset).all()
    session.close()

    if not data:
        return JSONResponse(status_code=400, content={"error": "No data available"})

    df = pd.DataFrame(
        [(d.feature1, d.feature2, d.target) for d in data],
        columns=["feature1", "feature2", "target"],
    )
    X = df[["feature1", "feature2"]]
    y = df["target"]

    model = LogisticRegression()
    model.fit(X, y)

    with mlflow.start_run() as run:
        mlflow.sklearn.log_model(model, "model")
        mlflow.log_param("dataset_size", len(df))
        logger.info(f"Model logged to run {run.info.run_id}")

    return {"message": "Model retrained and logged with MLflow"}


@router.get("/predict")
def predict():
    session = SessionLocal()
    last_row = session.query(Dataset).order_by(Dataset.id.desc()).first()
    session.close()

    if not last_row:
        return JSONResponse(
            status_code=400, content={"error": "No data available for prediction"}
        )

    model_uri = get_last_model_uri()
    if not model_uri:
        return JSONResponse(
            status_code=500, content={"error": "No model available. Retrain first."}
        )

    model = mlflow.sklearn.load_model(model_uri)

    input_vector = [last_row.feature1, last_row.feature2]
    X = pd.DataFrame([input_vector], columns=model.feature_names_in_)

    pred = model.predict(X)
    logger.info(f"Prédiction {int(pred[0])}")
    return {"prediction": int(pred[0])}
