
import getpass

from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError

from app.database import SessionLocal
from app.models import User, Role, UserRole
from app.auth import hash_password


def create_college_admin():
    username = input("Username: ").strip()
    email = input("Email: ").strip().lower()
    password = getpass.getpass("Password: ")
    confirm_password = getpass.getpass("Confirm password: ")

    if not username or not email or not password:
        print("Username, email, and password are required.")
        return

    if password != confirm_password:
        print("Passwords do not match.")
        return

    if len(password) < 12:
        print("Use a password with at least 12 characters.")
        return

    with SessionLocal() as db:
        try:
            role = db.scalar(
                select(Role).where(Role.name == "COLLEGE_ADMIN")
            )

            if role is None:
                print("COLLEGE_ADMIN role not found. Seed roles first.")
                return

            existing_admin_count = db.scalar(
                select(func.count())
                .select_from(UserRole)
                .where(UserRole.role_id == role.id)
            )

            if existing_admin_count:
                print("A college admin already exists.")
                return

            existing_user = db.scalar(
                select(User).where(
                    (User.username == username)
                    | (User.email == email)
                )
            )

            if existing_user:
                print("Username or email already exists.")
                return

            user = User(
                username=username,
                email=email,
                hashed_password=hash_password(password),
                is_active=True,
            )

            db.add(user)
            db.flush()

            db.add(
                UserRole(
                    user_id=user.id,
                    role_id=role.id,
                    hostel_id=None,
                    assigned_by=None,
                )
            )

            db.commit()
            print("College admin created successfully.")

        except IntegrityError:
            db.rollback()
            print("Account creation failed due to a database constraint.")


if __name__ == "__main__":
    create_college_admin()
