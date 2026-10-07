# SuperKart sales forecasting API (Flask)

import os

import joblib
import pandas as pd
from flask import Flask, jsonify, request

# Initialize the Flask application
superkart_api = Flask("SuperKart Sales Forecaster")

# Load the serialized pipeline (preprocessing + model) from the same folder as this file
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "superkart_model.joblib")
model = joblib.load(MODEL_PATH)

# Feature columns expected by the model, in training order
FEATURES = [
    "Product_Weight",
    "Product_Sugar_Content",
    "Product_Allocated_Area",
    "Product_MRP",
    "Store_Size",
    "Store_Location_City_Type",
    "Store_Type",
    "Product_Id_char",
    "Store_Age_Years",
    "Product_Type_Category",
]


@superkart_api.get("/")
def home():
    """Health-check endpoint."""
    return "Welcome to the SuperKart Sales Forecasting API!"


@superkart_api.post("/v1/predict")
def predict_sales():
    """Online inference: predict sales for a single product-store record sent as JSON."""
    record = request.get_json(silent=True)
    if not isinstance(record, dict):
        return jsonify({"error": "Request body must be a JSON object."}), 400

    # Validate that every expected feature is present
    missing = [f for f in FEATURES if f not in record]
    if missing:
        return jsonify({"error": f"Missing features: {missing}"}), 400

    # Build a one-row DataFrame in the expected column order and predict
    input_df = pd.DataFrame([{f: record[f] for f in FEATURES}])
    prediction = float(model.predict(input_df)[0])

    return jsonify({"Predicted_Sales": round(prediction, 2)})


@superkart_api.post("/v1/predictbatch")
def predict_sales_batch():
    """Batch inference: predict sales for every row of an uploaded CSV file."""
    if "file" not in request.files:
        return jsonify({"error": "Upload a CSV file in the 'file' field."}), 400

    input_df = pd.read_csv(request.files["file"])

    # Validate that every expected feature is present
    missing = [f for f in FEATURES if f not in input_df.columns]
    if missing:
        return jsonify({"error": f"Missing features: {missing}"}), 400

    predictions = model.predict(input_df[FEATURES])

    # Map each row index to its predicted sales value
    output = {str(idx): round(float(pred), 2) for idx, pred in zip(input_df.index, predictions)}
    return jsonify(output)


# Run the development server when executed directly (gunicorn is used inside Docker)
if __name__ == "__main__":
    superkart_api.run(host="0.0.0.0", port=7860, debug=False)
