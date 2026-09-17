from flask import Flask, render_template, request, jsonify

import pandas as pd
import joblib
import os

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor


# ---------------------------------------------------------
# Flask application
# ---------------------------------------------------------

app = Flask(__name__)


# ---------------------------------------------------------
# File paths
# ---------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATASET_PATH = os.path.join(BASE_DIR, "dataset.csv")
MODEL_PATH = os.path.join(BASE_DIR, "house_model.pkl")


# ---------------------------------------------------------
# Load trained model
# ---------------------------------------------------------

model = joblib.load(MODEL_PATH)


# ---------------------------------------------------------
# Home page
# ---------------------------------------------------------

@app.route("/")
def home():

    return render_template("index.html")


# ---------------------------------------------------------
# Prediction API
# ---------------------------------------------------------

@app.route("/predict", methods=["POST"])
def predict():

    global model

    try:

        # Receive JSON from JavaScript
        data = request.get_json()

        # Create DataFrame
        input_data = pd.DataFrame([{
            "Location": data["location"],
            "Area": float(data["area"]),
            "Bedrooms": int(data["bedrooms"]),
            "Age": int(data["age"]),
            "Bathrooms": int(data["bathrooms"]),
            "Parking": data["parking"],
            "PropertyType": data["property_type"]
        }])

        # Predict
        prediction = model.predict(input_data)[0]

        # Return JSON
        return jsonify({
            "success": True,
            "prediction": round(float(prediction))
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 400


# ---------------------------------------------------------
# Feedback / correction API
# ---------------------------------------------------------

@app.route("/feedback", methods=["POST"])
def feedback():

    global model

    try:

        data = request.get_json()

        # ---------------------------------------------
        # Create corrected row
        # ---------------------------------------------

        new_row = {
            "Location": data["location"],
            "Area": float(data["area"]),
            "Bedrooms": int(data["bedrooms"]),
            "Age": int(data["age"]),
            "Bathrooms": int(data["bathrooms"]),
            "Parking": data["parking"],
            "PropertyType": data["property_type"],
            "Price": float(data["actual_price"])
        }

        # ---------------------------------------------
        # Load existing dataset
        # ---------------------------------------------

        df = pd.read_csv(DATASET_PATH)

        # ---------------------------------------------
        # Add new feedback row
        # ---------------------------------------------

        df = pd.concat(
            [df, pd.DataFrame([new_row])],
            ignore_index=True
        )

        # Save updated dataset
        df.to_csv(DATASET_PATH, index=False)

        # ---------------------------------------------
        # Prepare training data
        # ---------------------------------------------

        X = df.drop("Price", axis=1)

        y = df["Price"]

        categorical_features = [
            "Location",
            "Parking",
            "PropertyType"
        ]

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

        # ---------------------------------------------
        # Create new model
        # ---------------------------------------------

        new_model = Pipeline(
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

        # ---------------------------------------------
        # Retrain
        # ---------------------------------------------

        new_model.fit(X, y)

        # ---------------------------------------------
        # Save updated model
        # ---------------------------------------------

        joblib.dump(new_model, MODEL_PATH)

        # Update currently running model
        model = new_model

        return jsonify({
            "success": True,
            "message": "Thank you! Your correction was added and the model was retrained."
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 400


# ---------------------------------------------------------
# Start Flask
# ---------------------------------------------------------

if __name__ == "__main__":

    app.run(
        debug=True
    )