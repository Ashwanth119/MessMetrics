import requests
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select,delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import TestFood
from app.schemas import FoodItemCreate

task_routes = APIRouter(prefix="/tasks")


@task_routes.delete("/get/items_clear")
def clear_items(db: Session = Depends(get_db)):

    try:
        result = db.execute(delete(TestFood))

        deleted_count = result.rowcount

        db.commit()

        return {
            "message": "TestFood table cleared successfully",
            "deleted_records": deleted_count
        }

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not clear TestFood table"
        ) from exc











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

    # 1. Set request headers
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/154.0.0.0 Safari/537.36 Edg/154.0.0.0"
        )
    }

    # 2. Fetch mess menu API
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

    # 3. Validate API response
    if not isinstance(menu_data, list):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Menu API returned an unexpected response",
        )

    # 4. Extract all food items
    meals_times = ["breakfast", "lunch", "snacks", "dinner"]

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

            for times in meals_times:

                food = meal.get(times)

                if isinstance(food, str):

                    item_names.update(
                        name.strip()
                        for name in food.replace(",", "\n").splitlines()
                        if name.strip()
                    )
    # return item_names
    # 5. Find items already present in database
    existing_names: set[str] = set()

    if item_names:

        existing_names = set(
            db.scalars(
                select(TestFood.name).where(
                    TestFood.name.in_(item_names)
                )
            ).all()
        )

    # 6. Identify new food items
    new_names = item_names - existing_names

    new_items = [
        TestFood(name=name)
        for name in sorted(new_names)
    ]

    # 7. Insert new items into database
    if new_items:

        db.add_all(new_items)

        try:
            db.commit()

        except IntegrityError as exc:
            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="One or more food records already exist",
            ) from exc

    # 8. Return insertion summary
    return {
        "total_unique_items_found": len(item_names),
        "already_existing_items": len(existing_names),
        "new_items_inserted": len(new_items),
        "inserted_items": sorted(new_names),
        "existing_items": sorted(existing_names),
    }
