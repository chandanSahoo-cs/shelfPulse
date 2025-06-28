from db import SessionLocal
from models import Product, Prediction
from predict import predict_single_product
import pandas as pd
from sqlalchemy.exc import SQLAlchemyError

def run_batch_prediction_and_cache():
    db = SessionLocal()
    try:
        products = db.query(Product).all()

        for product in products:
            # Extract product data into a dict (excluding SQLAlchemy internals)
            row_dict = {
                k: v for k, v in product.__dict__.items()
                if not k.startswith("_") and k not in ["id", "sku", "predictions"]
            }
            row_df = pd.DataFrame([row_dict])

            # Predict using your existing function
            pred = predict_single_product(row_df)

            # Mark existing latest prediction as old
            db.query(Prediction).filter(
                Prediction.product_id == product.id,
                Prediction.is_latest == True
            ).update({Prediction.is_latest: False})

            # Create and store new prediction
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
        print("✅ Cached predictions updated for all products.")

    except SQLAlchemyError as e:
        db.rollback()
        print("❌ Database error during caching:", e)

    finally:
        db.close()


if __name__ == "__main__":
    run_batch_prediction_and_cache()
