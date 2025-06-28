from db import SessionLocal
from models import Product, Prediction
from predict import predict_single_product
import pandas as pd

def run_batch_prediction_and_cache():
    db = SessionLocal()
    products = db.query(Product).all()

    for product in products:
        # Prepare product data as DataFrame
        row_dict = {
            k: v for k, v in product.__dict__.items()
            if not k.startswith("_") and k not in ["id", "sku", "predictions"]
        }
        row_df = pd.DataFrame([row_dict])

        # Run prediction
        pred = predict_single_product(row_df)

        # Mark old predictions as not latest
        db.query(Prediction).filter(
            Prediction.product_id == product.id,
            Prediction.is_latest == True
        ).update({Prediction.is_latest: False})

        # Insert new prediction
        new_pred = Prediction(
            product_id=product.id,
            spoilage_risk=pred["spoilage_risk"],
            days_to_expiry_pred=pred["days_to_expiry"],
            forecasted_demand_pred=pred["forecasted_demand"],
            dead_stock=pred["dead_stock"],
            trigger_markdown=pred["trigger_markdown"],
            sustainability_label=pred["sustainability_label"],
            is_latest=True
        )

        db.add(new_pred)

    db.commit()
    db.close()
    print("✅ Cached predictions updated with is_latest = True")

if __name__ == "__main__":
    run_batch_prediction_and_cache()
