from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import pandas as pd
from pathlib import Path

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "car_prediction_data.csv"

df = pd.read_csv(DATA_PATH)


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
    <head>
        <title>CARML</title>
        <style>
            body{
                font-family: Arial;
                max-width:800px;
                margin:auto;
                padding:20px;
            }
            input{
                padding:8px;
                margin:5px;
            }
            button{
                padding:10px;
            }
        </style>
    </head>
    <body>

        <h1>🚗 CARML</h1>
        <h3>Car Recommendation System</h3>

        <form action="/search">

            <label>Minimum Budget (Lakhs)</label><br>
            <input type="number" step="0.1" name="min_budget" required>

            <br><br>

            <label>Maximum Budget (Lakhs)</label><br>
            <input type="number" step="0.1"