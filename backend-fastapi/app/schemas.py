from datetime import date, datetime
from sqlalchemy import (
    Column, Integer, String, Float, ForeignKey
)
from typing import Optional, Literal
from sqlalchemy.orm import relationship
from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=8, max_length=128)


class UserUpdate(BaseModel):
    username: str | None = Field(
        default=None, min_length=3, max_length=50
    )
    email: str | None = Field(
        default=None, min_length=5, max_length=255
    )
    password: str | None = Field(
        default=None, min_length=8, max_length=128
    )


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class HostelAdminRegister(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=8, max_length=128)
    hostel_number: str = Field(pattern=r"^h([1-9]|1[0-9]|2[0-2])$")
    admin_type: str = Field(min_length=1, max_length=50)


class StudentRegister(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=100)
    roll_number: str = Field(min_length=1, max_length=30)
    hostel_number: str = Field(pattern=r"^[hH]([1-9]|1[0-9]|2[0-2])$")
    room_number: str = Field(min_length=1, max_length=20)
    date_of_birth: date | None = None
    height_cm: float | None = Field(default=None, gt=0)
    weight_kg: float | None = Field(default=None, gt=0)
    sex: Literal["female", "male"] | None = None
    activity_level: str | None = None


class ActivityLevelUpdate(BaseModel):
    activity_level: Literal["sedentary", "light", "moderate", "very_active", "extra_active"]



class MealLogItemInput(BaseModel):
    mess_menu_id: int = Field(gt=0)
    servings_consumed: float = Field(gt=0)


class MealLogUpsert(BaseModel):
    log_date: date
    meal_type: Literal["BREAKFAST", "LUNCH", "SNACKS", "DINNER"]
    items: list[MealLogItemInput] = Field(default_factory=list)


class MealLogItemResponse(BaseModel):
    id: int
    mess_menu_id: int | None
    food_name: str
    servings_consumed: float
    calories: float | None
    protein_g: float | None
    carbohydrates_total_g: float | None
    sugar_g: float | None
    fiber_g: float | None
    fat_total_g: float | None
    fat_saturated_g: float | None
    cholesterol_mg: float | None
    sodium_mg: float | None
    potassium_mg: float | None

    model_config = ConfigDict(from_attributes=True)


class MealLogResponse(BaseModel):
    id: int
    log_date: date
    meal_type: str
    items: list[MealLogItemResponse]

    model_config = ConfigDict(from_attributes=True)

