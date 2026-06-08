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
    <!DOCTYPE html>
    <html>
    <head>
        <title>CARML</title>
    </head>
    <body>
        <h1>🚗 CARML</h1>
        <h2>Car Recommendation System</h2>

        <form action="/search" method="get">

            <label>Minimum Budget:</label><br>
            <input type="number"
                   step="0.1"
                   name="min_budget"
                   required>

            <br><br>

            <label>Maximum Budget:</label><br>
            <input type="number"
                   step="0.1"
                   name="max_budget"
                   required>

            <br><br>

            <button type="submit">
                Search Cars
            </button>

        </form>

    </body>
    </html>
    """


@app.get("/search", response_class=HTMLResponse)
def search(min_budget: float, max_budget: float):

    cars = df[
        (df["Selling_Price"] >= min_budget)
        &
        (df["Selling_Price"] <= max_budget)
    ]

    html = """
    <html>
    <body>

    <h1>Matching Cars</h1>

    <table border="1">
    <tr>
        <th>Car</th>
        <th>Price</th>
        <th>KMs</th>
    </tr>
    """

    for _, row in cars.iterrows():
        html += f"""
        <tr>
            <td>{row['Car_Name']}</td>
            <td>{row['Selling_Price']}</td>
            <td>{row['Kms_Driven']}</td>
        </tr>
        """

    html += """
    </table>

    <br><br>

    <a href="/">Back</a>

    </body>
    </html>
    """

    return html