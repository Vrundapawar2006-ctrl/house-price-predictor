"""
train_model.py

This file:
1. Creates a dummy house-price dataset.
2. Converts categorical data into numbers.
3. Trains a machine learning regression model.
4. Saves the trained model as house_model.pkl.

Run this file once before starting Flask.
"""

import os
import random

import pandas as pd
import joblib

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor


# ---------------------------------------------------------
# 1. Project paths
# ---------------------------------------------------------

# Go one folder up from /model
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATASET_PATH = os.path.join(BASE_DIR, "dataset.csv")
MODEL_PATH = os.path.join(BASE_DIR, "house_model.pkl")


# ---------------------------------------------------------
# 2. Generate dummy dataset
# ---------------------------------------------------------

def generate_dataset(number_of_rows=500):
    """
    Generate synthetic house-price data.

    This is NOT real market data.
    It is only for demonstrating the ML application.
    """

    locations = [
        "City Center",
        "Suburbs",
        "Downtown"
    ]

    property_types = [
        "Flat",
        "Row House",
        "Bungalow"
    ]

    data = []

    for _ in range(number_of_rows):

        location = random.choice(locations)

        area = random.randint(500, 3000)

        bedrooms = random.randint(1, 5)

        age = random.randint(0, 30)

        bathrooms = random.randint(1, 4)

        parking = random.choice(["Yes", "No"])

        property_type = random.choice(property_types)

        # -------------------------------------------------
        # Synthetic pricing formula
        # -------------------------------------------------

        price = area * 4500

        # Location adjustment
        if location == "Downtown":
            price += 1500000

        elif location == "City Center":
            price += 1000000

        else:
            price += 300000

        # Bedrooms
        price += bedrooms * 500000

        # Bathrooms
        price += bathrooms * 250000

        # Parking
        if parking == "Yes":
            price += 300000

        # Property type
        if property_type == "Row House":
            price += 1000000

        elif property_type == "Bungalow":
            price += 2500000

        # Older houses are slightly cheaper
        price -= age * 50000

        # Add random variation
        price += random.randint(-500000, 500000)

        # Don't allow negative price
        price = max(price, 1000000)

        data.append({
            "Location": location,
            "Area": area,
            "Bedrooms": bedrooms,
            "Age": age,
            "Bathrooms": bathrooms,
            "Parking": parking,
            "PropertyType": property_type,
            "Price": round(price)
        })

    return pd.DataFrame(data)


# ---------------------------------------------------------
# 3. Train model
# ---------------------------------------------------------

def train_model():

    print("Generating dataset...")

    df = generate_dataset(500)

    # Save dataset
    df.to_csv(DATASET_PATH, index=False)

    print(f"Dataset saved to: {DATASET_PATH}")

    # -----------------------------------------------------
    # Separate inputs and output
    # -----------------------------------------------------

    X = df.drop("Price", axis=1)

    y = df["Price"]

    # -----------------------------------------------------
    # Identify categorical and numerical columns
    # -----------------------------------------------------

    categorical_features = [
        "Location",
        "Parking",
        "PropertyType"
    ]

    numerical_features = [
        "Area",
        "Bedrooms",
        "Age",
        "Bathrooms"
    ]

    # -----------------------------------------------------
    # Convert categorical values to numbers
    # -----------------------------------------------------

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                categorical_features
            )
        ],
        remainder="passthrough"
    )

    # -----------------------------------------------------
    # Create ML pipeline
    # -----------------------------------------------------

    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "regressor",
                RandomForestRegressor(
                    n_estimators=150,
                    random_state=42
                )
            )
        ]
    )

    # -----------------------------------------------------
    # Train
    # -----------------------------------------------------

    print("Training model...")

    model.fit(X, y)

    # -----------------------------------------------------
    # Save model
    # -----------------------------------------------------

    joblib.dump(model, MODEL_PATH)

    print(f"Model saved to: {MODEL_PATH}")

    print("\nTraining completed successfully!")


# ---------------------------------------------------------
# Program entry point
# ---------------------------------------------------------

if __name__ == "__main__":
    train_model()