import requests
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import TestFood
from app.schemas import FoodItemCreate

task_routes = APIRouter(prefix="/tasks")


@task_routes.post("/create/items", status_code=status.HTTP_201_CREATED)
def create_item(body: FoodItemCreate, db: Session = Depends(get_db)):
    existing_item = db.scalar(
        select(TestFood).where(TestFood.name == body.name.strip())
    )
    if existing_item:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Test food already exists",
        )

    item = TestFood(name=body.name.strip())
    db.add(item)
    try:
        db.commit()
        db.refresh(item)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Test food already exists",
        ) from exc

    return {"id": item.id, "name": item.name}


@task_routes.post("/get/items_inserted")
def insert_items(db: Session = Depends(get_db)):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/154.0.0.0 Safari/537.36 Edg/154.0.0.0"
        )
    }

    try:
        response = requests.get(
            "https://gymkhana.iitb.ac.in/instiapp/api/mess",
            headers=headers,
            timeout=15,
        )
        response.raise_for_status()
        menu_data = response.json()
    except (requests.RequestException, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not retrieve valid menu data",
        ) from exc

    if not isinstance(menu_data, list):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Menu API returned an unexpected response",
        )

    item_names: set[str] = set()
    for group in menu_data:
        if not isinstance(group, dict):
            continue
        meals = group.get("mess", [])
        if not isinstance(meals, list):
            continue
        for meal in meals:
            if not isinstance(meal, dict):
                continue
            breakfast = meal.get("breakfast")
            if isinstance(breakfast, str):
                item_names.update(
                    name.strip()
                    for name in breakfast.replace(",", "\n").splitlines()
                    if name.strip()
                )

    existing_names: set[str] = set()
    if item_names:
        existing_names = set(
            db.scalars(
                select(TestFood.name).where(TestFood.name.in_(item_names))
            ).all()
        )

    new_items = [
        TestFood(name=name)
        for name in sorted(item_names - existing_names)
    ]
    if new_items:
        db.add_all(new_items)
        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="One or more test food records already exist",
            ) from exc

    return {
        "inserted": len(new_items),
        "skipped_existing": len(item_names & existing_names),
    }
