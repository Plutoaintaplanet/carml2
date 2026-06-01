# /// script
# dependencies = [
#   "fastapi",
#   "uvicorn",
#   "pandas",
#   "scikit-learn",
# ]
# ///

import os
import pandas as pd
from pathlib import Path
from typing import Optional, List
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "car_prediction_data.csv"
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(title="CarML API", description="Car Selling Price Prediction & Depreciation Forecast API")

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for model and data
model = None
df = None
model_metrics = {"r2_score": 0.0, "mae": 0.0}

CSV_PATH = "car_prediction_data.csv"
CURRENT_YEAR = 2025

def train_model():
    global model, df, model_metrics
    
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"Dataset not found at {CSV_PATH}")
        
    df = pd.read_csv(CSV_PATH)
    
    # Feature Engineering (Age & Depreciation)
    # Note: If 'Year' exists, transform it to 'Car_Age' and drop 'Year'
    df["Car_Age"] = CURRENT_YEAR - df["Year"]
    df["Depreciation"] = df["Present_Price"] - df["Selling_Price"]
    
    # We will preserve df_clean for training
    df_train = df.copy()
    df_train.drop("Year", axis=1, inplace=True, errors='ignore')
    
    X = df_train.drop(["Selling_Price", "Depreciation"], axis=1)
    y = df_train["Depreciation"]
    
    cat_cols = ["Car_Name", "Fuel_Type", "Seller_Type", "Transmission"]
    num_cols = ["Present_Price", "Kms_Driven", "Owner", "Car_Age"]
    
    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown='ignore'), cat_cols),
            ("num", "passthrough", num_cols)
        ]
    )
    
    model = Pipeline([
        ("prep", preprocessor),
        ("reg", LinearRegression())
    ])
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    model_metrics["r2_score"] = round(r2_score(y_test, y_pred), 4)
    model_metrics["mae"] = round(mean_absolute_error(y_test, y_pred), 4)
    print(f"Model trained successfully. R2: {model_metrics['r2_score']}, MAE: {model_metrics['mae']}")

# Train the model on startup
@app.on_event("startup")
def startup_event():
    train_model()

# Schemas
class ForecastRequest(BaseModel):
    Car_Name: str
    Present_Price: float
    Kms_Driven: float
    Fuel_Type: str
    Seller_Type: str
    Transmission: str
    Owner: int
    Car_Age: int
    Annual_Running: float

class PredictRequest(BaseModel):
    Car_Name: str
    Present_Price: float
    Kms_Driven: float
    Year: int
    Fuel_Type: str
    Seller_Type: str
    Transmission: str
    Owner: int

# API Endpoints
@app.get("/api/stats")
def get_stats():
    global df
    if df is None:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    total_records = len(df)
    avg_selling_price = float(df["Selling_Price"].mean())
    avg_present_price = float(df["Present_Price"].mean())
    avg_kms_driven = float(df["Kms_Driven"].mean())
    avg_car_age = float(df["Car_Age"].mean())
    
    unique_cars = df["Car_Name"].unique().tolist()
    fuel_types = df["Fuel_Type"].unique().tolist()
    transmissions = df["Transmission"].unique().tolist()
    seller_types = df["Seller_Type"].unique().tolist()
    
    # Get top 5 most frequent car names
    top_cars = df["Car_Name"].value_counts().head(5).index.tolist()
    
    # Get some sample rows to display
    sample_cars = df.sample(min(8, len(df)), random_state=42).to_dict(orient="records")
    
    return {
        "total_records": total_records,
        "avg_selling_price": round(avg_selling_price, 2),
        "avg_present_price": round(avg_present_price, 2),
        "avg_kms_driven": int(avg_kms_driven),
        "avg_car_age": round(avg_car_age, 1),
        "unique_cars_count": len(unique_cars),
        "unique_cars": sorted(unique_cars),
        "top_cars": top_cars,
        "fuel_types": fuel_types,
        "transmissions": transmissions,
        "seller_types": seller_types,
        "samples": sample_cars
    }

@app.get("/api/model_info")
def get_model_info():
    return {
        "metrics": model_metrics,
        "status": "active",
        "algorithm": "Linear Regression (Scikit-Learn Pipeline)",
        "features": {
            "categorical": ["Car_Name", "Fuel_Type", "Seller_Type", "Transmission"],
            "numerical": ["Present_Price", "Kms_Driven", "Owner", "Car_Age"]
        }
    }

@app.get("/api/cars")
def get_cars(
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    fuel_type: Optional[str] = None,
    transmission: Optional[str] = None,
    search: Optional[str] = None
):
    global df
    if df is None:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    filtered_df = df.copy()
    
    if min_price is not None:
        filtered_df = filtered_df[filtered_df["Selling_Price"] >= min_price]
    if max_price is not None:
        filtered_df = filtered_df[filtered_df["Selling_Price"] <= max_price]
    if fuel_type and fuel_type != "All":
        filtered_df = filtered_df[filtered_df["Fuel_Type"].str.lower() == fuel_type.lower()]
    if transmission and transmission != "All":
        filtered_df = filtered_df[filtered_df["Transmission"].str.lower() == transmission.lower()]
    if search:
        filtered_df = filtered_df[filtered_df["Car_Name"].str.contains(search, case=False)]
        
    # Sort by Kms_Driven ascending (matching main.py)
    filtered_df = filtered_df.sort_values(by="Kms_Driven", ascending=True)
    
    # Return limited results or all
    results = filtered_df.to_dict(orient="records")
    return results

@app.post("/api/forecast")
def generate_forecast(req: ForecastRequest):
    global model
    if model is None:
        raise HTTPException(status_code=500, detail="Model not trained")
    
    base_kms = req.Kms_Driven
    base_age = req.Car_Age
    present_price = req.Present_Price
    
    forecast_results = []
    
    for year in range(1, 6):
        future_kms = base_kms + req.Annual_Running * year
        future_age = base_age + year
        
        # Build evaluation dataframe matching training features
        temp = pd.DataFrame([{
            "Car_Name": req.Car_Name,
            "Present_Price": req.Present_Price,
            "Kms_Driven": future_kms,
            "Fuel_Type": req.Fuel_Type,
            "Seller_Type": req.Seller_Type,
            "Transmission": req.Transmission,
            "Owner": req.Owner,
            "Car_Age": future_age
        }])
        
        predicted_dep = float(model.predict(temp)[0])
        future_value = present_price - predicted_dep
        
        if future_value < 0:
            future_value = 0.0
            
        forecast_results.append({
            "year": year,
            "age": future_age,
            "kms": int(future_kms),
            "predicted_depreciation": round(predicted_dep, 2),
            "estimated_value": round(future_value, 2)
        })
        
    return {
        "car_name": req.Car_Name,
        "base_year_price": present_price,
        "forecast": forecast_results
    }

@app.post("/api/predict")
def predict_custom_car(req: PredictRequest):
    global model
    if model is None:
        raise HTTPException(status_code=500, detail="Model not trained")
        
    car_age = CURRENT_YEAR - req.Year
    if car_age < 0:
        car_age = 0
        
    temp = pd.DataFrame([{
        "Car_Name": req.Car_Name,
        "Present_Price": req.Present_Price,
        "Kms_Driven": req.Kms_Driven,
        "Fuel_Type": req.Fuel_Type,
        "Seller_Type": req.Seller_Type,
        "Transmission": req.Transmission,
        "Owner": req.Owner,
        "Car_Age": car_age
    }])
    
    predicted_dep = float(model.predict(temp)[0])
    predicted_selling_price = req.Present_Price - predicted_dep
    
    # Sanity checks
    if predicted_selling_price < 0:
        predicted_selling_price = 0.0
    if predicted_selling_price > req.Present_Price:
        predicted_selling_price = req.Present_Price
        predicted_dep = 0.0
        
    dep_percentage = (predicted_dep / req.Present_Price * 100) if req.Present_Price > 0 else 0.0
    
    return {
        "car_age": car_age,
        "predicted_depreciation": round(predicted_dep, 2),
        "predicted_selling_price": round(predicted_selling_price, 2),
        "depreciation_percentage": round(dep_percentage, 1)
    }

@app.post("/api/retrain")
def retrain_endpoint():
    try:
        train_model()
        return {"status": "success", "metrics": model_metrics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount static files at /
# Create the frontend directory if it doesn't exist
os.makedirs(FRONTEND_DIR, exist_ok=True)
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
