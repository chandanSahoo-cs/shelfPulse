from flask import Flask, request, jsonify
import pickle
import numpy as np
import os

app = Flask(__name__)

# Load models
def load_model(name):
    with open(f"models/{name}", "rb") as f:
        return pickle.load(f)

spoilage_model = load_model("spoilage_model.pkl")
spoilage_encoder = load_model("spoilage_encoder.pkl")

expiry_model = load_model("expiry_model.pkl")
demand_model = load_model("demand_model.pkl")
dead_stock_model = load_model("dead_stock_model.pkl")
markdown_model = load_model("markdown_model.pkl")

sustainability_model = load_model("sustainability_model.pkl")
sustainability_encoder = load_model("sustainability_encoder.pkl")

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json

    try:
        # Convert input to model-ready numpy array
        # Ensure the order of features is consistent with training
        spoilage_features = np.array([
            data["Historical_Sell_Through"],
            data["Forecasted_Demand"],
            data["Spoilage_Risk_Score"],
            data["Cold_Chain_Energy_Use"],
            data["Sensor_Anomalies"],
            data["Markdown_History"],
            data["Transport_Emissions"],
            data["Recyclability_Score"],
            data["Overstock_Risk"],
            data["Stockout_Risk"],
            data["Waste_Risk_Index"]
        ]).reshape(1, -1)

        expiry_features = np.array([
            data["Historical_Sell_Through"],
            data["Forecasted_Demand"],
            data["Spoilage_Risk_Score"],
            data["Cold_Chain_Energy_Use"],
            data["Sensor_Anomalies"],
            data["Markdown_History"],
            data["Transport_Emissions"],
            data["Recyclability_Score"],
            data["Overstock_Risk"],
            data["Stockout_Risk"],
            data["Waste_Risk_Index"]
        ]).reshape(1, -1)

        demand_features = np.array([
            data["Historical_Sell_Through"],
            data["Days_to_Expiry"],
            data["Spoilage_Risk_Score"],
            data["Sensor_Anomalies"],
            data["Holiday_Demand_Amplifier"],
            data["Upcoming_Local_Events"],
            data["Promo_Effectiveness"],
            data["Festival_Sales_Boost"],
            data["Stockout_Risk"],
            data["Overstock_Risk"],
            data["Recyclability_Score"],
            data["Markdown_History"]
        ]).reshape(1, -1)

        dead_stock_features = np.array([
            data["Days_Since_Last_Sale"],
            data["Average_Turnover_Time"],
            data["Promo_Effectiveness"],
            data["Redundancy_Index"],
            data["Forecasted_Demand"],
            data["Historical_Sell_Through"],
            data["Shelf_Space_Efficiency"],
            data["Recyclability_Score"],
            data["Overstock_Risk"],
            data["Stockout_Risk"]
        ]).reshape(1, -1)

        markdown_features = np.array([
            data["Spoilage_Risk_Score"],
            data["Days_to_Expiry"],
            data["Overstock_Risk"],
            data["Historical_Sell_Through"],
            data["Forecasted_Demand"],
            data["Dead_Inventory_Flag"],
            data["Promo_Effectiveness"],
            data["Cold_Chain_Energy_Use"],
            data["Sensor_Anomalies"],
            data["Waste_Risk_Index"]
        ]).reshape(1, -1)

        sustainability_features = np.array([
            data["Embedded_Carbon_Footprint"],
            data["Cold_Chain_Energy_Use"],
            data["Transport_Emissions"],
            data["Recycled_Content_Pct"],
            data["Recyclability_Score"],
            data["Compostability_Score"],
            data["Take_Back_Eligible"],
            data["Footprint_Factor"]
        ]).reshape(1, -1)

        # Predictions
        spoilage_pred = spoilage_encoder.inverse_transform(spoilage_model.predict(spoilage_features))[0]
        expiry_pred = int(expiry_model.predict(expiry_features)[0])
        demand_pred = round(float(demand_model.predict(demand_features)[0]), 2)
        dead_stock_pred = bool(dead_stock_model.predict(dead_stock_features)[0])
        markdown_pred = bool(markdown_model.predict(markdown_features)[0])
        sustainability_pred = sustainability_encoder.inverse_transform(sustainability_model.predict(sustainability_features))[0]

        return jsonify({
            "spoilage_risk": spoilage_pred,
            "days_to_expiry": expiry_pred,
            "forecasted_demand": demand_pred,
            "dead_stock": dead_stock_pred,
            "trigger_markdown": markdown_pred,
            "sustainability_label": sustainability_pred
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
