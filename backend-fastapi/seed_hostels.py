
from app.database import Base, engine, SessionLocal
from app.models import Hostel


def seed_hostels():
    # Create tables that do not already exist.
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        for number in range(1, 23):
            hostel_number = f"H{number}"

            existing = (
                db.query(Hostel)
                .filter(
                    Hostel.hostel_number == hostel_number
                )
                .first()
            )

            if existing is None:
                db.add(
                    Hostel(
                        hostel_number=hostel_number,
                        name=f"Hostel {number}",
                    )
                )

        db.commit()

    print("Hostels H1 through H22 are ready.")


if __name__ == "__main__":
    seed_hostels()
