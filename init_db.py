from db import engine
from models import Base

# Create the tables
Base.metadata.create_all(bind=engine)
print("Database schema created")
