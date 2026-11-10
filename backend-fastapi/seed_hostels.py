
from app.database import Base, engine, SessionLocal
from app.models import Hostel, HostelMess, Mess


HOSTELS = [
    (f"H{number}", f"Hostel {number}")
    for number in range(1, 23)
] + [
    ("QIP", "QIP"),
    ("TANSA", "Tansa"),
]


def seed_hostels():
    # Create tables that do not already exist.
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        for hostel_number, hostel_name in HOSTELS:
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
                        name=hostel_name,
                    )
                )

        db.flush()

        for hostel in db.query(Hostel).all():
            existing_mapping = (
                db.query(HostelMess)
                .filter(HostelMess.hostel_id == hostel.id)
                .first()
            )
            if existing_mapping is not None:
                continue

            mess_name = f"{hostel.name} Mess"
            mess = db.query(Mess).filter(Mess.name == mess_name).first()
            if mess is None:
                mess = Mess(name=mess_name)
                db.add(mess)
                db.flush()

            db.add(HostelMess(hostel_id=hostel.id, mess_id=mess.id))

        db.commit()

    print("Menu hostels and their mess mappings are ready.")


if __name__ == "__main__":
    seed_hostels()
