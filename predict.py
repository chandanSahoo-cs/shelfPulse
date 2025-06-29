import joblib
import pandas as pd

# -------------------------------
# Load All Models and Encoders
# -------------------------------
spoilage_model = joblib.load("models/spoilage_model.pkl")
spoilage_encoder = joblib.load("models/spoilage_encoder.pkl")

expiry_model = joblib.load("models/expiry_model.pkl")
demand_model = joblib.load("models/demand_model.pkl")

dead_stock_model = joblib.load("models/dead_stock_model.pkl")
markdown_percent_model = joblib.load("models/markdown_percent_model.pkl")

sustain_model = joblib.load("models/sustainability_model.pkl")
sustain_encoder = joblib.load("models/sustainability_encoder.pkl")

# -------------------------------
# Prediction Function
# -------------------------------

def predict_single_product(row: pd.DataFrame) -> dict:
    """
    Accepts a single-row DataFrame of product features.
    Returns dictionary of all 6 predictions.
    """
    # Ensure exactly one row
    if row.shape[0] != 1:
        raise ValueError("Input must be a single-row DataFrame.")

    # Predict spoilage risk label
    spoilage_label = spoilage_encoder.inverse_transform(
        spoilage_model.predict(row[spoilage_model.feature_names_in_])
    )[0]

    # Predict expiry (regression)
    days_to_expiry = int(round(expiry_model.predict(row[expiry_model.feature_names_in_])[0]))

    # Predict demand (regression)
    forecasted_demand = round(float(demand_model.predict(row[demand_model.feature_names_in_])[0]), 3)

    # Predict dead stock (classification)
    dead_flag = bool(dead_stock_model.predict(row[dead_stock_model.feature_names_in_])[0])

    # Predict markdown percentage
    suggested_percent = round(float(markdown_percent_model.predict(
        row[markdown_percent_model.feature_names_in_])[0]), 2)

    markdown_flag = suggested_percent > 0  # or set a threshold, like > 5%

    # Predict sustainability label
    sustain_label = sustain_encoder.inverse_transform(
        sustain_model.predict(row[sustain_model.feature_names_in_])
    )[0]

    return {
        "spoilage_risk": spoilage_label,
        "days_to_expiry": days_to_expiry,
        "forecasted_demand": forecasted_demand,
        "dead_stock": dead_flag,
        "trigger_markdown": markdown_flag,
        "suggested_markdown_percent": suggested_percent,
        "sustainability_label": sustain_label
    }
