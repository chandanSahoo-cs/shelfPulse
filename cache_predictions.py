from db import SessionLocal
from models import Product, Prediction
from predict import predict_single_product
import pandas as pd
from sqlalchemy.exc import SQLAlchemyError

def run_batch_prediction_and_cache():
    db = SessionLocal()
    success_count = 0
    failure_count = 0

    try:
        products = db.query(Product).all()

        for product in products:
            try:
                # Prepare product data as a row dict
                row_dict = {
                    k: v for k, v in product.__dict__.items()
                    if not k.startswith("_") and k not in ["id", "sku", "predictions"]
                }
                row_df = pd.DataFrame([row_dict])

                # Run prediction
                pred = predict_single_product(row_df)
                print(f"🧠 Prediction for {product.sku} → {pred}")

                # Mark old predictions as not latest
                db.query(Prediction).filter(
                    Prediction.product_id == product.id,
                    Prediction.is_latest == True
                ).update({Prediction.is_latest: False}, synchronize_session=False)

                # Create new prediction
                new_pred = Prediction(
                    product_id=product.id,
                    spoilage_risk=str(pred["spoilage_risk"]),
                    days_to_expiry_pred=int(pred["days_to_expiry"]),
                    forecasted_demand_pred=float(pred["forecasted_demand"]),
                    dead_stock=bool(pred["dead_stock"]),
                    suggested_markdown_percent=float(pred["suggested_markdown_percent"]),
                    trigger_markdown=bool(pred["trigger_markdown"]),
                    sustainability_label=str(pred["sustainability_label"]),
                    is_latest=True
                )

                db.add(new_pred)
                print(f"✅ New prediction added for {product.sku}")
                success_count += 1

            except Exception as inner_e:
                print(f"❌ Failed to predict for product SKU: {product.sku} — {inner_e}")
                failure_count += 1

        db.commit()
        print(f"🎯 Batch Prediction Summary → Success: {success_count}, Failed: {failure_count}")

    except SQLAlchemyError as db_error:
        db.rollback()
        print("❌ Fatal DB error during prediction run:", db_error)

    finally:
        db.close()

if __name__ == "__main__":
    run_batch_prediction_and_cache()
