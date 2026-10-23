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


class HostelAdminRequest(Base):
    __tablename__ = "hostel_admin_requests"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )

    hostel_id: Mapped[int] = mapped_column(
        ForeignKey("hostels.id"),
        nullable=False
    )

    admin_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="PENDING",
        server_default="PENDING"
    )

    reviewed_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )

    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )