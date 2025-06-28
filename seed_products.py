import numpy as np
from db import SessionLocal
from models import Product

np.random.seed(42)
db = SessionLocal()

for i in range(100):
    product = Product(
        sku=f"SKU-{1000 + i}",
        Historical_Sell_Through=np.random.uniform(0.1, 1.0),
        Spoilage_Risk_Score=np.random.uniform(0, 1),
        Cold_Chain_Energy_Use=np.random.uniform(0, 5),
        Sensor_Anomalies=np.random.randint(0, 10),
        Markdown_History=np.random.randint(0, 5),
        Transport_Emissions=np.random.uniform(0.1, 10),
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
        Days_to_Expiry=np.random.randint(1, 15),
        Forecasted_Demand=np.random.uniform(0.2, 2.0),
        Dead_Inventory_Flag=np.random.randint(0, 2)
    )
    db.add(product)

db.commit()
db.close()
print("✅ Seeded 100 mock products into the database.")
