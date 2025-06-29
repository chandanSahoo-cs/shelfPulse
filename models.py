from sqlalchemy import Column, Integer, Float, String, Boolean, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from db import Base

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    sku = Column(String, unique=True, nullable=False)

    # Features
    Historical_Sell_Through = Column(Float)
    Spoilage_Risk_Score = Column(Float)
    Cold_Chain_Energy_Use = Column(Float)
    Sensor_Anomalies = Column(Integer)
    Markdown_History = Column(Integer)
    Transport_Emissions = Column(Float)
    Recyclability_Score = Column(Float)
    Overstock_Risk = Column(Float)
    Stockout_Risk = Column(Float)
    Embedded_Carbon_Footprint = Column(Float)
    Recycled_Content_Pct = Column(Float)
    Compostability_Score = Column(Float)
    Take_Back_Eligible = Column(Integer)
    Footprint_Factor = Column(Float)
    Holiday_Demand_Amplifier = Column(Float)
    Upcoming_Local_Events = Column(Integer)
    Promo_Effectiveness = Column(Float)
    Festival_Sales_Boost = Column(Float)
    Days_Since_Last_Sale = Column(Integer)
    Average_Turnover_Time = Column(Float)
    Redundancy_Index = Column(Float)
    Shelf_Space_Efficiency = Column(Float)
    Waste_Risk_Index = Column(Float)
    Days_to_Expiry = Column(Integer)
    Forecasted_Demand = Column(Float)
    Dead_Inventory_Flag = Column(Integer)

    predictions = relationship("Prediction", back_populates="product")


class Prediction(Base):
    __tablename__ = 'predictions'

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    product = relationship("Product", back_populates="predictions")

    spoilage_risk = Column(String)
    days_to_expiry_pred = Column(Integer)
    forecasted_demand_pred = Column(Float)
    dead_stock = Column(Boolean)

    # ✅ Replaced logic
    suggested_markdown_percent = Column(Float)
    trigger_markdown = Column(Boolean)  # Optional: keep if needed for API filtering

    sustainability_label = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_latest = Column(Boolean, default=True)
