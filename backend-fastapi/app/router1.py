import requests
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
import os
from app.database import get_db
from app.models1 import Food,FoodAlias,FoodNutrition
from app.schemas import FoodItemCreate
from rapidfuzz import fuzz
from dotenv import load_dotenv

load_dotenv()
task_routes = APIRouter(prefix="/tasks")


@task_routes.get("/get_calories_per_person")
def calculate_calories(age, height, weight, sex, activity):
    # Calculate BMR
    if sex.lower() == "male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    elif sex.lower() == "female":
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    else:
        raise ValueError("sex must be 'male' or 'female'")

    # Calculate TDEE
    activity_factors = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "very_active": 1.725,
        "extra_active": 1.9
    }

    if activity not in activity_factors:
        raise ValueError("Invalid activity level")

    tdee = bmr * activity_factors[activity]

    return {
        "bmr": round(bmr),
        "maintenance_calories": round(tdee)
    }


# result = calculate_calories(
#     age=22,
#     height=175,
#     weight=75,
#     sex="male",
#     activity="moderate"
# )

# print(result)



@task_routes.post("/create/items", status_code=status.HTTP_201_CREATED)
def create_item(body: FoodItemCreate, db: Session = Depends(get_db)):
    existing_item = db.scalar(
        select(Food).where(Food.name == body.name.strip())
    )
    if existing_item:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Test food already exists",
        )

    item = Food(name=body.name.strip())
    # db.add(item)
    # try:
    #     db.commit()
    #     db.refresh(item)
    # except IntegrityError as exc:
    #     db.rollback()
    #     raise HTTPException(
    #         status_code=status.HTTP_409_CONFLICT,
    #         detail="Test food already exists",
    #     ) from exc
    response = insert_food_nutrition(db, body.name.strip())
    
    return {"id": item.id, "name": item.name, "response":response}


def get_data():
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
    return menu_data

def extract_items(menu_data):

    item_names = set()
    meals_times = ["breakfast"]

    for i in menu_data:
        for j in i['mess']:
            for meal in meals_times:
                item_names.update(
                    name.strip()
                    for name in j.get(meal, "").replace(",", "\n").splitlines()
                    if name.strip()
                )

    return item_names


def group_similar_items(item_names):

    similar_items = []
    visited = set()

    item_names = sorted(item_names)

    for i, item in enumerate(item_names):

        if item in visited:
            continue

        group = [item]
        visited.add(item)

        for other in item_names[i + 1:]:

            if other not in visited:

                score = fuzz.token_sort_ratio(
                    item.lower(), other.lower()
                )

                if score >= 85:
                    group.append(other)
                    visited.add(other)

        similar_items.append(group)

    return similar_items


def insert_food(db: Session, canonical_name):

    food = db.scalar(
        select(Food).where(
            Food.name == canonical_name
        )
    )

    if not food:
        food = Food(name=canonical_name)
        db.add(food)
        db.flush()

        return food, True

    return food, False


# 4. Insert food aliases
def insert_aliases(db: Session, group, food_id):

    inserted_aliases = []

    for name in group[1:]:

        existing_alias = db.scalar(
            select(FoodAlias).where(
                FoodAlias.food_name == name
            )
        )

        if not existing_alias:

            db.add(
                FoodAlias(
                    food_name=name,
                    food_id=food_id
                )
            )

            inserted_aliases.append(name)

        elif existing_alias.food_id != food_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"{name} is already linked to another food"
            )

    return inserted_aliases


@task_routes.post("/get/items_inserted")
def insert_items(db: Session = Depends(get_db)):

    menu_data = get_data()

    # Extract items
    item_names = extract_items(menu_data)

    # Group similar items
    similar_items = group_similar_items(item_names)

    inserted_foods = []
    inserted_aliases = []

    try:

        for group in similar_items:

            canonical_name = group[0]

            # Insert canonical food
            food, is_new = insert_food(
                db, canonical_name
            )

            if is_new:
                inserted_foods.append(canonical_name)

            # Insert aliases
            aliases = insert_aliases(
                db,
                group,
                food.id
            )

            inserted_aliases.extend(aliases)

        db.commit()

    except IntegrityError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="One or more food records already exist"
        ) from exc

    except Exception:
        db.rollback()
        raise

    return {
        "total_unique_items_found": len(item_names),
        "similar_groups": similar_items,
        "new_foods_inserted": len(inserted_foods),
        "new_aliases_inserted": len(inserted_aliases),
        "inserted_foods": inserted_foods,
        "inserted_aliases": inserted_aliases
    }

def get_food_id(db: Session, name):

    # Check canonical food
    food = db.query(Food).filter(
        Food.name.ilike(name)
    ).first()

    if food:
        return food.id

    # Check alias
    alias = db.query(FoodAlias).filter(
        FoodAlias.food_name.ilike(name)
    ).first()

    if alias:
        return alias.food_id

    return None

def insert_food_nutrition(db: Session, query):
    API_KEY = os.getenv("CALORIE_NINJA_API_KEY")
    api_url = 'https://api.calorieninjas.com/v1/nutrition?query='
    response = requests.get(api_url + query, headers={'X-Api-Key': API_KEY})
    if response.status_code != requests.codes.ok:
        print("Error:", response.status_code, response.text)
    return response.text