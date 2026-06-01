import pandas as pd
import time
import sys
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "car_prediction_data.csv"


# ---------------------------
# Progress Bar
# ---------------------------
def progress_bar(task, steps=30, delay=0.03):
    print(f"\n{task}")
    for i in range(steps + 1):
        percent = int((i / steps) * 100)
        bar = "█" * i + "-" * (steps - i)
        sys.stdout.write(f"\r[{bar}] {percent}%")
        sys.stdout.flush()
        time.sleep(delay)
    print(" Done ✓")


# ---------------------------
# Load Dataset
# ---------------------------
print("Loading Dataset...")
progress_bar("Reading Data")

df = pd.read_csv(DATA_PATH)

# ---------------------------
# Feature Engineering
# ---------------------------
current_year = 2025

df["Car_Age"] = current_year - df["Year"]

df["Depreciation"] = (
    df["Present_Price"] - df["Selling_Price"]
)

df.drop("Year", axis=1, inplace=True)

print("\nRecords:", len(df))

progress_bar("Preprocessing Data")


# ---------------------------
# Features / Target
# ---------------------------
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


# ---------------------------
# Preprocessing
# ---------------------------
preprocessor = ColumnTransformer(
    transformers=[
        (
            "cat",
            OneHotEncoder(handle_unknown='ignore'),
            cat_cols
        ),
        (
            "num",
            "passthrough",
            num_cols
        )
    ]
)


# ---------------------------
# Model
# ---------------------------
model = Pipeline([
    ("prep", preprocessor),
    ("reg", LinearRegression())
])


# ---------------------------
# Train/Test Split
# ---------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

progress_bar("Training Model")

model.fit(X_train, y_train)

progress_bar("Evaluating Model")

y_pred = model.predict(X_test)


# ---------------------------
# Metrics
# ---------------------------
print("\n===== MODEL LOGS =====")

print(
    "R2 Score:",
    round(r2_score(y_test, y_pred), 3)
)

print(
    "MAE:",
    round(mean_absolute_error(y_test, y_pred), 3)
)


# ---------------------------
# Budget Filter
# ---------------------------
print("\n===== FIND CARS =====")

low = float(input("Minimum Budget (Lakhs): "))
high = float(input("Maximum Budget (Lakhs): "))

progress_bar("Searching Cars", 20)

cars = df[
    (df["Selling_Price"] >= low)
    &
    (df["Selling_Price"] <= high)
]

cars = cars.sort_values(
    by="Kms_Driven",
    ascending=True
).reset_index(drop=True)

if len(cars) < 3:
    print("\nNeed at least 3 cars in selected budget range.")
    exit()

print("\nAvailable Cars (Lower KM first):\n")

for i, row in cars.iterrows():
    print(
        f"{i+1}. "
        f"{row['Car_Name']} | "
        f"{round(row['Selling_Price'], 2)} Lakhs | "
        f"KM: {int(row['Kms_Driven'])}"
    )


# ---------------------------
# Select 3 Cars
# ---------------------------
print("\n===== SELECT 3 CARS TO COMPARE =====")

selected_cars = []

for pick in range(3):
    while True:
        try:
            choice = int(input(f"\nSelect car #{pick+1} number: "))

            if choice < 1 or choice > len(cars):
                print("Invalid selection.")
                continue

            annual_run = int(
                input(
                    f"Annual Running for car #{pick+1} (km/year): "
                )
            )

            selected = cars.iloc[choice - 1]

            selected_cars.append({
                "car": selected,
                "annual_run": annual_run
            })

            break

        except ValueError:
            print("Enter valid numeric input.")


progress_bar("Comparing Cars", 30)


# ---------------------------
# Forecast Comparison
# ---------------------------
comparison_results = []

for item in selected_cars:
    selected = item["car"]
    annual_run = item["annual_run"]

    base_age = selected["Car_Age"]
    base_kms = selected["Kms_Driven"]
    present = selected["Present_Price"]

    final_value = 0
    total_dep = 0

    print(f"\n===== FORECAST: {selected['Car_Name']} =====")

    for year in range(1, 6):
        future_kms = base_kms + (annual_run * year)

        temp = pd.DataFrame([{
            "Car_Name": selected["Car_Name"],
            "Present_Price": selected["Present_Price"],
            "Kms_Driven": future_kms,
            "Fuel_Type": selected["Fuel_Type"],
            "Seller_Type": selected["Seller_Type"],
            "Transmission": selected["Transmission"],
            "Owner": selected["Owner"],
            "Car_Age": base_age + year
        }])

        predicted_dep = model.predict(temp)[0]

        future_value = present - predicted_dep

        if future_value < 0:
            future_value = 0

        total_dep = predicted_dep
        final_value = future_value

        print(f"\nYear {year}")
        print("Car Age:", base_age + year)
        print("KM Driven:", int(future_kms))
        print("Predicted Depreciation:", round(predicted_dep, 2), "Lakhs")
        print("Estimated Value:", round(future_value, 2), "Lakhs")


    # Buy Score Logic
    score = (
        (final_value * 0.6)
        -
        (total_dep * 0.3)
        -
        (((annual_run * 5) / 100000) * 0.1)
    )

    comparison_results.append({
        "Car_Name": selected["Car_Name"],
        "Selling_Price": selected["Selling_Price"],
        "Final_Value_5Y": round(final_value, 2),
        "Depreciation_5Y": round(total_dep, 2),
        "KM_After_5Y": int(base_kms + (annual_run * 5)),
        "Score": round(score, 3)
    })


# ---------------------------
# Comparison Summary
# ---------------------------
compare_df = pd.DataFrame(comparison_results)

print("\n===== COMPARISON SUMMARY =====")
print(compare_df)


# ---------------------------
# Best Buy Decision
# ---------------------------
best = compare_df.sort_values(
    by="Score",
    ascending=False
).iloc[0]

print("\n===== BEST BUY RECOMMENDATION =====")

print("Recommended Car:", best["Car_Name"])
print("Current Price:", best["Selling_Price"], "Lakhs")
print("Estimated 5-Year Value:", best["Final_Value_5Y"], "Lakhs")
print("Expected Depreciation:", best["Depreciation_5Y"], "Lakhs")
print("Buy Score:", best["Score"])


# ---------------------------
# Inference
# ---------------------------
print("\n===== INFERENCE =====")

print(
    f"{best['Car_Name']} is the best buy because it achieves "
    f"the highest ownership score among the compared cars."
)

print(
    "Decision factors considered:"
)

print("- Better resale value retention")
print("- Lower depreciation impact")
print("- Lower long-term usage penalty")
print("- Better 5-year ownership economics")

print("\nForecast Completed ✓")