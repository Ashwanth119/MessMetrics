from datetime import datetime

from sqlalchemy import String, Boolean, DateTime, Integer, func, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column


from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )

    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255), nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class Hostel(Base):
    __tablename__ = "hostels"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    hostel_number: Mapped[str] = mapped_column(
        String(5), unique=True, nullable=False, index=True
    )

    name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    name: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )

    description: Mapped[str] = mapped_column(
        String(255), nullable=False
    )


class UserRole(Base):
    __tablename__ = "user_roles"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "role_id",
            "hostel_id",
            name="uq_user_role_hostel",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id"),
        nullable=False,
    )

    hostel_id: Mapped[int | None] = mapped_column(
        ForeignKey("hostels.id"),
        nullable=True,
    )

    # Used for HOSTEL_ADMIN roles:
    # WARDEN, MESS_INCHARGE, etc.
    admin_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    assigned_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


