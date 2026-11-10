from app.database import Base, engine
from app import models, models1

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("Database tables checked.")
