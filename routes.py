from flask import Blueprint, request, jsonify, send_file
from db import SessionLocal
from models import Product, Prediction
from predict import predict_single_product
import pandas as pd
import tempfile
from cache_predictions import run_batch_prediction_and_cache

router = Blueprint("router", __name__)

# -----------------------
# Util: Safe type parser
# -----------------------
def _parse_value(val):
    try:
        return int(val)
    except:
        try:
            return float(val)
        except:
            if val.lower() == "true":
                return True
            if val.lower() == "false":
                return False
            return val

# -----------------------
# 1. Predict Single JSON
# -----------------------
@router.route("/api/v1/predict", methods=["POST"])
def predict_api():
    try:
        json_data = request.get_json()
        if not json_data:
            return jsonify({"error": "No JSON received"}), 400

        df = pd.DataFrame([json_data])
        result = predict_single_product(df)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -----------------------
# 2. Predict from CSV
# -----------------------
@router.route("/api/v1/predict_csv", methods=["POST"])
def predict_csv():
    if "file" not in request.files:
        return jsonify({"error": "CSV file is required under 'file' field"}), 400

    file = request.files["file"]

    try:
        df = pd.read_csv(file)

        if df.empty:
            return jsonify({"error": "CSV is empty"}), 400

        results = []
        for _, row in df.iterrows():
            row_df = pd.DataFrame([row])
            prediction = predict_single_product(row_df)
            results.append(prediction)

        output_df = pd.concat([df.reset_index(drop=True), pd.DataFrame(results)], axis=1)

        # Save to temp file
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
        output_path = tmp.name
        output_df.to_csv(output_path, index=False)
        tmp.close()

        return send_file(output_path, as_attachment=True, download_name="predicted_output.csv", mimetype='text/csv')

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -----------------------
# 3. Get Product by SKU
# -----------------------
@router.route("/api/v1/product/<sku>", methods=["GET"])
def get_product_by_sku(sku):
    db = SessionLocal()
    product = db.query(Product).filter(Product.sku == sku).first()

    if not product:
        db.close()
        return jsonify({"error": "Product not found"}), 404

    prediction = db.query(Prediction).filter(
        Prediction.product_id == product.id,
        Prediction.is_latest == True
    ).first()

    db.close()

    return jsonify({
        "sku": product.sku,
        "features": {
            k: getattr(product, k)
            for k in product.__table__.columns.keys()
            if k not in ["id", "sku"]
        },
        "prediction": {
            k: getattr(prediction, k)
            for k in prediction.__table__.columns.keys()
            if k not in ["id", "product_id", "is_latest", "created_at"]
        }
    })

# -----------------------
# 4. Get Filtered Products (Mass Query)
# -----------------------
@router.route("/api/v1/products", methods=["GET"])
def get_filtered_products():
    db = SessionLocal()
    query = db.query(Product, Prediction).join(Prediction).filter(Prediction.is_latest == True)

    args = request.args

    product_fields = [c.name for c in Product.__table__.columns]
    prediction_fields = [c.name for c in Prediction.__table__.columns]

    for param, val in args.items():
        if param in product_fields:
            query = query.filter(getattr(Product, param) == _parse_value(val))
        elif param in prediction_fields:
            query = query.filter(getattr(Prediction, param) == _parse_value(val))
        elif param.endswith("_gt"):
            base = param[:-3]
            if base in product_fields:
                query = query.filter(getattr(Product, base) > _parse_value(val))
            elif base in prediction_fields:
                query = query.filter(getattr(Prediction, base) > _parse_value(val))
        elif param.endswith("_lt"):
            base = param[:-3]
            if base in product_fields:
                query = query.filter(getattr(Product, base) < _parse_value(val))
            elif base in prediction_fields:
                query = query.filter(getattr(Prediction, base) < _parse_value(val))

    limit = int(args.get("limit", 100))
    offset = int(args.get("offset", 0))
    query = query.limit(limit).offset(offset)

    results = query.all()
    db.close()

    return jsonify([
        {
            "sku": product.sku,
            "features": {
                k: getattr(product, k)
                for k in product.__table__.columns.keys()
                if k not in ["id", "sku"]
            },
            "prediction": {
                k: getattr(prediction, k)
                for k in prediction.__table__.columns.keys()
                if k not in ["id", "product_id", "is_latest", "created_at"]
            }
        }
        for product, prediction in results
    ])

#------------------
# Cache Prediction
#------------------
@router.route("/api/v1/run_cache", methods=["POST"])
def run_cache_from_api():
    try:
        run_batch_prediction_and_cache()
        return jsonify({"status": "success", "message": "Predictions cached and updated."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

#-------------
# Health Check
#-------------

@router.route("/", methods=["GET"])
def home():
    return "✅ ShelfPulse API is live"