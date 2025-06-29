import numpy as np
from db import SessionLocal
from models import Product

np.random.seed(42)

# Category-specific settings
CATEGORY_CONFIG = {
    "produce": {
        "Spoilage_Risk_Score": (0.6, 1.0),
        "Days_to_Expiry": (1, 5),
        "Transport_Emissions": (1.0, 5.0)
    },
    "dairy": {
        "Spoilage_Risk_Score": (0.4, 0.9),
        "Days_to_Expiry": (3, 10),
        "Transport_Emissions": (2.0, 6.0)
    },
    "bakery": {
        "Spoilage_Risk_Score": (0.2, 0.7),
        "Days_to_Expiry": (2, 7),
        "Transport_Emissions": (0.5, 3.0)
    },
    "frozen": {
        "Spoilage_Risk_Score": (0.0, 0.2),
        "Days_to_Expiry": (10, 30),
        "Transport_Emissions": (3.0, 8.0)
    },
    "beverage": {
        "Spoilage_Risk_Score": (0.1, 0.3),
        "Days_to_Expiry": (20, 60),
        "Transport_Emissions": (1.0, 4.0)
    },
    "furniture": {
        "Spoilage_Risk_Score": (0.0, 0.05),
        "Days_to_Expiry": (60, 365),
        "Transport_Emissions": (4.0, 10.0)
    },
    "utensils": {
        "Spoilage_Risk_Score": (0.0, 0.1),
        "Days_to_Expiry": (90, 730),
        "Transport_Emissions": (2.0, 6.0)
    }
}

CATEGORIES = list(CATEGORY_CONFIG.keys())

def generate_mock_products(n=100):
    products = []

    for i in range(n):
        category = np.random.choice(CATEGORIES)
        config = CATEGORY_CONFIG[category]

        product = Product(
            sku=f"SKU-{1000 + i}",
            category=category,
            Historical_Sell_Through=np.random.uniform(0.1, 1.0),
            Spoilage_Risk_Score=np.random.uniform(*config["Spoilage_Risk_Score"]),
            Cold_Chain_Energy_Use=np.random.uniform(0, 5),
            Sensor_Anomalies=np.random.randint(0, 10),
            Markdown_History=np.random.randint(0, 5),
            Transport_Emissions=np.random.uniform(*config["Transport_Emissions"]),
            Recyclability_Score=np.random.uniform(0, 1),
            Overstock_Risk=np.random.uniform(0, 1),
            Stockout_Risk=np.random.uniform(0, 1),
            Embedded_Carbon_Footprint=np.random.uniform(0.1, 10.0),
            Recycled_Content_Pct=np.random.uniform(0, 1),
            Compostability_Score=np.random.uniform(0, 1),
            Take_Back_Eligible=np.random.randint(0, 2),
            Footprint_Factor=np.random.uniform(0, 2),
            Holiday_Demand_Amplifier=np.random.uniform(0.8, 1.2),
            Upcoming_Local_Events=np.random.randint(0, 2),
            Promo_Effectiveness=np.random.uniform(0.5, 2.0),
            Festival_Sales_Boost=np.random.uniform(0.9, 1.5),
            Days_Since_Last_Sale=np.random.randint(0, 30),
            Average_Turnover_Time=np.random.uniform(2, 15),
            Redundancy_Index=np.random.uniform(0, 1),
            Shelf_Space_Efficiency=np.random.uniform(0, 1),
            Waste_Risk_Index=np.random.uniform(0, 1),
            Days_to_Expiry=np.random.randint(*config["Days_to_Expiry"]),
            Forecasted_Demand=np.random.uniform(0.2, 2.0),
            Dead_Inventory_Flag=np.random.randint(0, 2)
        )
        products.append(product)

    return products


if __name__ == "__main__":
    db = SessionLocal()
    try:
        mock_products = generate_mock_products(100)
        db.bulk_save_objects(mock_products)
        db.commit()
        print("Seeded 100 mock products into the database.")
    except Exception as e:
        db.rollback()
        print("Seeding failed:", e)
    finally:
        db.close()
