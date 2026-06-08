from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
import pandas as pd
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

app = FastAPI()

def page_style():
    return """
    <style>

    body {
        font-family: 'Segoe UI', sans-serif;
        background: linear-gradient(
            135deg,
            #050505,
            #111111,
            #1d1d1d
        );
        color: white;
        min-height: 100vh;
        max-width: 1400px;
        margin: auto;
        padding: 30px;
    }

    h1 {
        color: #ff2020;
        letter-spacing: 3px;
        text-transform: uppercase;
        text-shadow: 0 0 20px rgba(255,0,0,0.4);
    }

    h2 {
        color: #d8d8d8;
    }

    .card {
        background: rgba(255,255,255,0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 20px;
        padding: 25px;
        margin-top: 20px;
        box-shadow: 0 0 30px rgba(255,0,0,0.15);
    }

    table {
        width: 100%;
        border-collapse: collapse;
        background: rgba(255,255,255,0.05);
        backdrop-filter: blur(8px);
        border-radius: 15px;
        overflow: hidden;
    }

    th {
        background: linear-gradient(
            90deg,
            #8b0000,
            #ff0000
        );
        color: white;
        padding: 12px;
    }

    td {
        padding: 12px;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }

    tr:hover {
        background: rgba(255,0,0,0.08);
    }

    input {
        padding: 12px;
        border-radius: 10px;
        border: none;
        background: #222;
        color: white;
    }

    button {
        padding: 12px 24px;
        border-radius: 12px;
        border: none;
        background: linear-gradient(
            90deg,
            #ff0000,
            #990000
        );
        color: white;
        font-weight: bold;
        cursor: pointer;
        transition: 0.3s;
    }

    button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 20px rgba(255,0,0,0.6);
    }

    a {
        color: #ff5050;
        text-decoration: none;
    }

    a:hover {
        color: white;
    }

    .winner {
        margin-top: 30px;
        padding: 20px;
        border-radius: 20px;
        text-align: center;
        font-size: 2rem;
        color: gold;
        background: linear-gradient(
            135deg,
            #3d0000,
            #7a0000
        );
        box-shadow: 0 0 30px rgba(255,215,0,0.25);
    }

    </style>
    """

# -------------------------
# Load Dataset
# -------------------------

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "car_prediction_data.csv"

df = pd.read_csv(DATA_PATH)

# Fix corrupted CSV header if needed
if "winget install --id Git.Git -e --source wingetCar_Name" in df.columns:
    df.rename(
        columns={
            "winget install --id Git.Git -e --source wingetCar_Name": "Car_Name"
        },
        inplace=True
    )

# -------------------------
# Feature Engineering
# -------------------------

current_year = 2025

df["Car_Age"] = current_year - df["Year"]

df["Depreciation"] = (
    df["Present_Price"] - df["Selling_Price"]
)

# -------------------------
# Features / Target
# -------------------------

X = df.drop(
    ["Selling_Price", "Depreciation"],
    axis=1
)

y = df["Depreciation"]

cat_cols = [
    "Car_Name",
    "Fuel_Type",
    "Seller_Type",
    "Transmission"
]

num_cols = [
    "Present_Price",
    "Kms_Driven",
    "Owner",
    "Car_Age"
]

# -------------------------
# Preprocessor
# -------------------------

preprocessor = ColumnTransformer(
    transformers=[
        (
            "cat",
            OneHotEncoder(handle_unknown="ignore"),
            cat_cols
        ),
        (
            "num",
            "passthrough",
            num_cols
        )
    ]
)

# -------------------------
# Linear Regression Model
# -------------------------

model = Pipeline([
    ("prep", preprocessor),
    ("reg", LinearRegression())
])

# -------------------------
# Train Model
# -------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

model.fit(X_train, y_train)

r2 = r2_score(
    y_test,
    model.predict(X_test)
)

print("Model R2 Score:", round(r2, 3))

# -------------------------
# Home Page
# -------------------------

@app.get("/", response_class=HTMLResponse)
@app.get("/", response_class=HTMLResponse)
def home():
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>CARML</title>

        <style>

        body {{

            font-family: 'Segoe UI', sans-serif;

            background:
            linear-gradient(
                135deg,
                #050505,
                #111111,
                #1d1d1d
            );

            color: white;

            min-height: 100vh;

            max-width: 1200px;

            margin: auto;

            padding: 40px;
        }}

        h1 {{

            color: #ff2020;

            font-size: 3rem;

            letter-spacing: 4px;

            text-transform: uppercase;

            text-shadow:
                0 0 20px rgba(255,0,0,0.4);
        }}

        h2 {{

            color: #d8d8d8;
        }}

        p {{

            color: #c0c0c0;
        }}

        .card {{

            background:
                rgba(255,255,255,0.05);

            backdrop-filter:
                blur(10px);

            border:
                1px solid rgba(255,255,255,0.1);

            border-radius: 20px;

            padding: 30px;

            box-shadow:
                0 0 30px rgba(255,0,0,0.15);
        }}

        input {{

            width: 320px;

            padding: 12px;

            border-radius: 12px;

            border: none;

            background: #222;

            color: white;

            font-size: 16px;
        }}

        input:focus {{

            outline: none;

            box-shadow:
                0 0 15px rgba(255,0,0,0.5);
        }}

        button {{

            padding: 14px 30px;

            border: none;

            border-radius: 12px;

            background:
                linear-gradient(
                    90deg,
                    #ff0000,
                    #990000
                );

            color: white;

            font-weight: bold;

            cursor: pointer;

            transition: 0.3s;
        }}

        button:hover {{

            transform: scale(1.05);

            box-shadow:
                0 0 20px rgba(255,0,0,0.6);
        }}

        .metric {{

            font-size: 1.2rem;

            color: #ffd700;

            margin-bottom: 20px;
        }}

        </style>

    </head>

    <body>

        <h1>Car Recommendation System</h1>

        <h2>
            AI Powered Vehicle Ownership Analytics
        </h2>

        <p>
            Premium Depreciation Forecasting &
            5-Year Ownership Intelligence
        </p>

        <div class="card">

            <div class="metric">
                Linear Regression Model R² Score:
                <b>{round(r2,3)}</b>
            </div>

            <form action="/search">

                <label>Minimum Budget (Lakhs)</label>
                <br>

                <input
                    type="number"
                    step="0.1"
                    name="min_budget"
                    required>

                <br><br>

                <label>Maximum Budget (Lakhs)</label>
                <br>

                <input
                    type="number"
                    step="0.1"
                    name="max_budget"
                    required>

                <br><br>

                <button type="submit">
                    🔍 Search Cars
                </button>

            </form>

        </div>

    </body>
    </html>
    """

# -------------------------
# Search Cars
# -------------------------

@app.get("/search", response_class=HTMLResponse)
def search(min_budget: float, max_budget: float):

    cars = df[
        (df["Selling_Price"] >= min_budget)
        &
        (df["Selling_Price"] <= max_budget)
    ]

    html = f"""
    <html>
    <head>
    {page_style()}
    </head>
    <body>

    <h1>Select 3 Cars</h1>

    <p>Cars Found: <b>{len(cars)}</b></p>

    <form action="/compare" method="get">

    <table border="1" cellpadding="5">

    <tr>
        <th>Select</th>
        <th>Car Name</th>
        <th>Price</th>
        <th>KMs Driven</th>
        <th>Fuel Type</th>
    </tr>
    """

    for i, row in cars.iterrows():

        html += f"""
        <tr>

            <td>
                <input
                    type="checkbox"
                    name="car_ids"
                    value="{i}">
            </td>

            <td>{row['Car_Name']}</td>
            <td>{row['Selling_Price']}</td>
            <td>{row['Kms_Driven']}</td>
            <td>{row['Fuel_Type']}</td>

        </tr>
        """

    html += """
    </table>

    <br><br>

    Annual Running (KM / Year)

    <input
        type="number"
        name="annual_run"
        value="12000"
        required>

    <br><br>

    <button type="submit">
        Compare Cars
    </button>

    </form>

    <br><br>

    <a href="/">Back</a>

    </body>
    </html>
    """

    return html

# -------------------------
# Dataset Info
# -------------------------

@app.get("/count")
def count():
    return {
        "rows": len(df),
        "columns": list(df.columns)
    }

# -------------------------
# Sample Records
# -------------------------

@app.get("/sample")
def sample():
    return df.head(5).to_dict(orient="records")

# -------------------------
# Predict Depreciation
# -------------------------

@app.get("/predict")
def predict(
    car_name: str,
    present_price: float,
    kms_driven: int,
    fuel_type: str,
    seller_type: str,
    transmission: str,
    owner: int,
    car_age: int
):

    temp = pd.DataFrame([{
        "Car_Name": car_name,
        "Present_Price": present_price,
        "Kms_Driven": kms_driven,
        "Fuel_Type": fuel_type,
        "Seller_Type": seller_type,
        "Transmission": transmission,
        "Owner": owner,
        "Car_Age": car_age
    }])

    predicted_dep = model.predict(temp)[0]

    estimated_value = present_price - predicted_dep

    if estimated_value < 0:
        estimated_value = 0

    return {
        "predicted_depreciation": round(float(predicted_dep), 2),
        "estimated_value": round(float(estimated_value), 2),
        "r2_score": round(float(r2), 3)
    }

@app.get("/forecast")
def forecast(
    car_name: str,
    present_price: float,
    kms_driven: int,
    fuel_type: str,
    seller_type: str,
    transmission: str,
    owner: int,
    car_age: int,
    annual_run: int
):

    results = []

    for year in range(1, 6):

        future_kms = kms_driven + (annual_run * year)

        temp = pd.DataFrame([{
            "Car_Name": car_name,
            "Present_Price": present_price,
            "Kms_Driven": future_kms,
            "Fuel_Type": fuel_type,
            "Seller_Type": seller_type,
            "Transmission": transmission,
            "Owner": owner,
            "Car_Age": car_age + year
        }])

        predicted_dep = model.predict(temp)[0]

        future_value = present_price - predicted_dep

        if future_value < 0:
            future_value = 0

        results.append({
            "year": year,
            "car_age": car_age + year,
            "kms": int(future_kms),
            "predicted_depreciation": round(float(predicted_dep), 2),
            "estimated_value": round(float(future_value), 2)
        })

    return {
        "car": car_name,
        "forecast": results
    }

@app.get("/compare", response_class=HTMLResponse)
def compare(
    car_ids: list[int] = Query(...),
    annual_run: int = 12000
):

    if len(car_ids) != 3:
        return """
        <html>
        <body>
        <h1>Please select exactly 3 cars.</h1>
        <a href="/">Back</a>
        </body>
        </html>
        """

    html = """
    <html>
   
    <body>

    <h1>5-Year Comparison Results</h1>

    <table border="1" cellpadding="5">

    <tr>
        <th>Car</th>
        <th>Current Price</th>
        <th>KM After 5 Years</th>
        <th>Predicted Value</th>
        <th>Depreciation</th>
    </tr>
    """

    best_score = -999999
    best_car = ""

    for idx in car_ids:

        car = df.iloc[idx]

        future_kms = (
            car["Kms_Driven"]
            +
            annual_run * 5
        )

        temp = pd.DataFrame([{
            "Car_Name": car["Car_Name"],
            "Present_Price": car["Present_Price"],
            "Kms_Driven": future_kms,
            "Fuel_Type": car["Fuel_Type"],
            "Seller_Type": car["Seller_Type"],
            "Transmission": car["Transmission"],
            "Owner": car["Owner"],
            "Car_Age": car["Car_Age"] + 5
        }])

        depreciation = model.predict(temp)[0]

        future_value = (
            car["Present_Price"]
            -
            depreciation
        )

        if future_value < 0:
            future_value = 0

        score = future_value

        if score > best_score:
            best_score = score
            best_car = car["Car_Name"]

        html += f"""
        <tr>
            <td>{car['Car_Name']}</td>
            <td>{round(car['Selling_Price'], 2)}</td>
            <td>{future_kms}</td>
            <td>{round(future_value, 2)}</td>
            <td>{round(depreciation, 2)}</td>
        </tr>
        """

    html += f"""
    </table>

    <br><br>

    <h2>
    🏆 Best Buy Recommendation:
    {best_car}
    </h2>

    <br><br>

    <a href="/">Start Again</a>

    </body>
    </html>
    """

    return html