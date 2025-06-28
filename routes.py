from flask import Blueprint, request, jsonify, send_file
import pandas as pd
import tempfile
from predict import predict_single_product

router = Blueprint("router", __name__)

@router.route("/predict", methods=["POST"])
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


@router.route("/predict_csv", methods=["POST"])
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

        # Merge predictions
        output_df = pd.concat([df.reset_index(drop=True), pd.DataFrame(results)], axis=1)

        # Save to temp file
        import tempfile, os
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
        output_path = tmp.name
        output_df.to_csv(output_path, index=False)
        tmp.close()

        # ✅ This triggers actual download
        from flask import send_file
        return send_file(output_path, as_attachment=True, download_name="predicted_output.csv", mimetype='text/csv')

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@router.route("/product/<sku>", methods=["GET"])
def get_product_by_sku(sku):
    db = SessionLocal()
    product = db.query(Product).filter(Product.sku == sku).first()

    if not product:
        return jsonify({"error": "Product not found"}), 404

    prediction = db.query(Prediction).filter(
        Prediction.product_id == product.id,
        Prediction.is_latest == True
    ).first()

    db.close()

    return jsonify({
        "sku": product.sku,
        "features": {k: getattr(product, k) for k in product.__table__.columns.keys() if k not in ["id", "sku"]},
        "prediction": {k: getattr(prediction, k) for k in prediction.__table__.columns.keys() if k not in ["id", "product_id", "is_latest", "created_at"]}
    })

@router.route("/products", methods=["GET"])
def get_filtered_products():
    db = SessionLocal()
    query = db.query(Product, Prediction).join(Prediction).filter(Prediction.is_latest == True)

    args = request.args

    # Base field mappings
    product_fields = [c.name for c in Product.__table__.columns]
    prediction_fields = [c.name for c in Prediction.__table__.columns]

    # Support for exact and range filters
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

    # Pagination
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

def _parse_value(val):
    # Try int, then float, then keep as string
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