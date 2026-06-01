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


# Custom progress bar (no extra libraries)
def progress_bar(task, steps=30, delay=0.03):
    print(f"\n{task}")
    for i in range(steps + 1):
        percent = int((i / steps) * 100)
        bar = "█" * i + "-" * (steps - i)

        sys.stdout.write(
            f"\r[{bar}] {percent}%"
        )
        sys.stdout.flush()

        time.sleep(delay)

    print(" Done ✓")


print("Loading dataset...")
progress_bar("Reading Data")

df = pd.read_csv(DATA_PATH)

# Better feature than raw year
current_year = 2025
df["Car_Age"] = current_year - df["Year"]

# Remove Year after creating age
df.drop("Year", axis=1, inplace=True)

print("\nRecords:", len(df))

progress_bar("Preprocessing Data")

X = df.drop("Selling_Price", axis=1)
y = df["Selling_Price"]

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

model = Pipeline([
    ("prep", preprocessor),
    ("reg", LinearRegression())
])

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

progress_bar("Training Model")

model.fit(X_train, y_train)

progress_bar("Generating Predictions")

y_pred = model.predict(X_test)

print("\n===== TRAINING LOGS =====")

print(
    "R2 Score:",
    round(
        r2_score(y_test, y_pred),
        3
    )
)

print(
    "MAE:",
    round(
        mean_absolute_error(
            y_test,
            y_pred
        ),
        3
    )
)

print("\n===== VEHICLE RECOMMENDATION =====")

low = float(input("Minimum budget: "))
high = float(input("Maximum budget: "))

fuel = input(
    "Fuel Type(Petrol/Diesel/CNG): "
).strip().lower()

trans = input(
    "Transmission(Manual/Automatic): "
).strip().lower()

progress_bar("Searching Cars", 25, 0.04)

suggest = df[
    (df['Selling_Price'] >= low) &
    (df['Selling_Price'] <= high) &
    (df['Fuel_Type'].str.lower() == fuel) &
    (df['Transmission'].str.lower() == trans)
]

suggest = suggest[
    ['Car_Name', 'Selling_Price']
].drop_duplicates()

if len(suggest) > 0:

    print("\nSuggested Cars:\n")

    for _, row in suggest.head(5).iterrows():

        print(
            row['Car_Name'],
            "-",
            round(
                row['Selling_Price'],
                2
            ),
            "Lakhs"
        )

else:
    print("No matches found")