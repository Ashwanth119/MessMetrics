
from app.database import Base, engine, SessionLocal
from app.models import Role, User, Hostel, UserRole

ROLES = {
    "COLLEGE_ADMIN": "College-wide administrator",
    "HOSTEL_ADMIN": "Administrator for an assigned hostel",
    "STUDENT_COUNCIL": "Student council member",
    "STUDENT": "Regular student",
}


def seed_roles():
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        for name, description in ROLES.items():
            existing = (
                db.query(Role)
                .filter(Role.name == name)
                .first()
            )

            if existing is None:
                db.add(
                    Role(
                        name=name,
                        description=description,
                    )
                )

        db.commit()

    print("Roles are ready.")


if __name__ == "__main__":
    seed_roles()
