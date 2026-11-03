from datetime import date, datetime

from sqlalchemy import (
    String, Boolean, DateTime, Integer, Float, Date, func, ForeignKey, UniqueConstraint,
    Index, CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB


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


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    roll_number: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    hostel_id: Mapped[int] = mapped_column(ForeignKey("hostels.id"), nullable=False)
    room_number: Mapped[str] = mapped_column(String(20), nullable=False)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    height_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    activity_level: Mapped[str | None] = mapped_column(String(20), nullable=True)


class Mess(Base):
    __tablename__ = "messes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class HostelMess(Base):
    __tablename__ = "hostel_messes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    hostel_id: Mapped[int] = mapped_column(
        ForeignKey("hostels.id"),
        unique=True,
        nullable=False,
    )
    mess_id: Mapped[int] = mapped_column(
        ForeignKey("messes.id"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class FoodItem(Base):
    __tablename__ = "food_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    serving_size_g: Mapped[float | None] = mapped_column(Float, nullable=True)
    calories: Mapped[float | None] = mapped_column(Float, nullable=True)
    protein_g: Mapped[float | None] = mapped_column(Float, nullable=True)
    carbohydrates_total_g: Mapped[float | None] = mapped_column(Float, nullable=True)
    sugar_g: Mapped[float | None] = mapped_column(Float, nullable=True)
    fiber_g: Mapped[float | None] = mapped_column(Float, nullable=True)
    fat_total_g: Mapped[float | None] = mapped_column(Float, nullable=True)
    fat_saturated_g: Mapped[float | None] = mapped_column(Float, nullable=True)
    cholesterol_mg: Mapped[float | None] = mapped_column(Float, nullable=True)
    sodium_mg: Mapped[float | None] = mapped_column(Float, nullable=True)
    potassium_mg: Mapped[float | None] = mapped_column(Float, nullable=True)
    nutrition_source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    nutrition_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class MenuUpdateBatch(Base):
    __tablename__ = "menu_update_batches"
    __table_args__ = (
        CheckConstraint(
            "source_type IN ('INSTIAPP_AUTO', 'HOSTEL_ADMIN', 'STUDENT_COUNCIL')",
            name="ck_menu_batch_source_type",
        ),
        CheckConstraint(
            "status IN ('SUCCESS', 'PARTIAL', 'FAILED')",
            name="ck_menu_batch_status",
        ),
        Index("ix_menu_batch_started_at", "started_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source_type: Mapped[str] = mapped_column(String(30), nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    updated_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="SUCCESS", nullable=False)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)


class MessMenu(Base):
    __tablename__ = "mess_menus"
    __table_args__ = (
        UniqueConstraint(
            "mess_id",
            "food_item_id",
            "menu_date",
            "meal_type",
            name="uq_mess_menu_food_date_meal",
        ),
        CheckConstraint(
            "meal_type IN ('BREAKFAST', 'LUNCH', 'SNACKS', 'DINNER')",
            name="ck_mess_menu_meal_type",
        ),
        CheckConstraint(
            "serving_quantity IS NULL OR serving_quantity > 0",
            name="ck_mess_menu_serving_quantity",
        ),
        Index("ix_mess_menu_date_meal", "menu_date", "meal_type"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    mess_id: Mapped[int] = mapped_column(ForeignKey("messes.id"), nullable=False)
    food_item_id: Mapped[int] = mapped_column(ForeignKey("food_items.id"), nullable=False)
    menu_date: Mapped[date] = mapped_column(Date, nullable=False)
    meal_type: Mapped[str] = mapped_column(String(20), nullable=False)
    serving_quantity: Mapped[float | None] = mapped_column(Float, nullable=True)
    serving_unit: Mapped[str | None] = mapped_column(String(20), nullable=True)
    source_batch_id: Mapped[int | None] = mapped_column(
        ForeignKey("menu_update_batches.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class MenuSourceSnapshot(Base):
    __tablename__ = "menu_source_snapshots"
    __table_args__ = (
        CheckConstraint(
            "meal_type IN ('BREAKFAST', 'LUNCH', 'SNACKS', 'DINNER')",
            name="ck_menu_snapshot_meal_type",
        ),
        Index("ix_menu_snapshot_hostel_date", "hostel_id", "menu_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    batch_id: Mapped[int] = mapped_column(
        ForeignKey("menu_update_batches.id", ondelete="CASCADE"),
        nullable=False,
    )
    hostel_id: Mapped[int] = mapped_column(ForeignKey("hostels.id"), nullable=False)
    menu_date: Mapped[date] = mapped_column(Date, nullable=False)
    meal_type: Mapped[str] = mapped_column(String(20), nullable=False)
    raw_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class MenuChangeLog(Base):
    __tablename__ = "menu_change_logs"
    __table_args__ = (
        CheckConstraint(
            "action IN ('INSERT', 'UPDATE', 'DELETE')",
            name="ck_menu_change_action",
        ),
        Index("ix_menu_change_batch", "batch_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    batch_id: Mapped[int] = mapped_column(
        ForeignKey("menu_update_batches.id", ondelete="CASCADE"),
        nullable=False,
    )
    mess_menu_id: Mapped[int | None] = mapped_column(
        ForeignKey("mess_menus.id", ondelete="SET NULL"),
        nullable=True,
    )
    action: Mapped[str] = mapped_column(String(10), nullable=False)
    old_values: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    new_values: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)