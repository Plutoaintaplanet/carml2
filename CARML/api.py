from fastapi import FastAPI
import pandas as pd
from pathlib import Path

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "car_prediction_data.csv"

df = pd.read_csv(DATA_PATH)

@app.get("/")
def home():
    return {
        "message": "CARML API Running"
    }

@app.get("/cars")
def get_cars(min_budget: float, max_budget: float):

    cars = df[
        (df["Selling_Price"] >= min_budget)
        &
        (df["Selling_Price"] <= max_budget)
    ]

    cars = cars.sort_values(
        by="Kms_Driven",
        ascending=True
    )

    return cars.head(20).to_dict(orient="records")