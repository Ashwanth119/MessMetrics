from datetime import datetime
import requests
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
import os
import re
from datetime import date, timedelta
from app.database import get_db
from app.models import FoodItem,HostelMess,Hostel,MessMenu
# from app.models1 import Food,FoodAlias,FoodNutrition
# from app.schemas import FoodItemCreate
# from rapidfuzz import fuzz
from dotenv import load_dotenv

load_dotenv()
task_routes = APIRouter(prefix="/tasks")

@task_routes.put("/modify/existing_data")
def modify_existing_food_nutrition(db: Session = Depends(get_db)):
    nutrition_fields = (
        "serving_size_g",
        "calories",
        "protein_g",
        "carbohydrates_total_g",
        "sugar_g",
        "fiber_g",
        "fat_total_g",
        "fat_saturated_g",
        "cholesterol_mg",
        "sodium_mg",
        "potassium_mg",
    )
    foods = db.query(FoodItem).filter(
        or_(*(getattr(FoodItem, field).is_(None) for field in nutrition_fields))
    ).order_by(FoodItem.id).all()

    updated_foods = []
    try:
        for food in foods:
            nutrition = insert_food_nutrition(food.name)
            for field in nutrition_fields:
                setattr(food, field, nutrition.get(field))
            food.nutrition_updated_at=datetime.now()
            updated_foods.append({"id": food.id, "name": food.name})
        db.commit()
    except Exception:
        db.rollback()
        raise

    return {
        "message": "Existing food nutrition updated successfully",
        "updated_count": len(updated_foods),
        "updated_foods": updated_foods,
    }


@task_routes.delete("/delete/all-food-items")
def delete_all_food_items(db: Session = Depends(get_db)):

    try:
        deleted_count = db.query(FoodItem).delete(
            synchronize_session=False
        )

        db.commit()

        return {
            "message": "All food items deleted successfully",
            "deleted_count": deleted_count
        }

    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete food items"
        ) from exc


@task_routes.get("/get_calories_per_person")
def calculate_calories(age_years, height_cm, weight_kg, sex, activity_level):
    age_years = int(age_years)
    height_cm = int(height_cm)
    weight_kg = int(weight_kg)

    if sex.lower() == "male":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age_years + 5
    elif sex.lower() == "female":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age_years - 161
    else:
        raise ValueError("sex must be 'male' or 'female'")

    activity_factors = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "very_active": 1.725,
        "extra_active": 1.9
    }

    activity_level = activity_level.lower()

    if activity_level not in activity_factors:
        raise ValueError("Invalid activity level")

    tdee = bmr * activity_factors[activity_level]

    return {
        "bmr": int(round(bmr)),
        "maintenance_calories": int(round(tdee))
    }

# result = calculate_calories(
#     age=22,
#     height=175,
#     weight=75,
#     sex="male",
#     activity="moderate"
# )

# print(result)



# @task_routes.post("/create/items", status_code=status.HTTP_201_CREATED)
# def create_item(body: FoodItemCreate, db: Session = Depends(get_db)):
#     existing_item = db.scalar(
#         select(Food).where(Food.name == body.name.strip())
#     )
#     if existing_item:
#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail="Test food already exists",
#         )

#     item = Food(name=body.name.strip())
#     # db.add(item)
#     # try:
#     #     db.commit()
#     #     db.refresh(item)
#     # except IntegrityError as exc:
#     #     db.rollback()
#     #     raise HTTPException(
#     #         status_code=status.HTTP_409_CONFLICT,
#     #         detail="Test food already exists",
#     #     ) from exc
#     response = insert_food_nutrition(db, body.name.strip())
    
#     return {"id": item.id, "name": item.name, "response":response}


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

def extract_items(menu_data, db: Session):

    meals_times = ["breakfast", "lunch", "snacks", "dinner"]

    results = []

    today = date.today()

    last_saturday = today - timedelta(
        days=(today.weekday() - 5) % 7
    )

    for i in menu_data:

        hostel_name = i.get("name", "")
        mess_id = (
            db.query(HostelMess.mess_id)
            .join(Hostel, Hostel.id == HostelMess.hostel_id)
            .filter(Hostel.name == hostel_name)
            .scalar()
        )

        for j in i.get("mess", []):
            try:
                day_number = int(j["day"])
            except (KeyError, TypeError, ValueError) as exc:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Menu API returned a menu without a valid day",
                ) from exc

            if not 1 <= day_number <= 7:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Menu API returned a menu with an invalid day",
                )

            ans = {
                "Hostel_name": hostel_name,
                "menu_date": last_saturday + timedelta(days=day_number),
                "mess_id": mess_id,
                "times": {},
            }

            for meal in meals_times:

                raw_items = j.get(meal, "")

                # Clean food items here
                cleaned_items = clean_food_items(raw_items)

                if meal not in ans["times"]:
                    ans["times"][meal] = []

                for item_name in cleaned_items:

                    if item_name.lower() not in [
                        x.lower() for x in ans["times"][meal]
                    ]:
                        ans["times"][meal].append(item_name)

            results.append(ans)

    return results

def clean_food_items(text):

    if not text:
        return []

    # Remove schedule labels
    text = re.sub(
        r'\b(?:'
        r'odd\s+week|even\s+week|'
        r'week\s*\d+|'
        r'\d+(?:st|nd|rd|th)\s+week|'
        r'alternate\s+weeks?|'
        r'every\s+week|'
        r'weekdays?|weekends?|'
        r'monday|tuesday|wednesday|thursday|friday|saturday|sunday|'
        r'daily|weekly|optional|special|'
        r'breakfast|lunch|dinner'
        r')\s*:',
        '',
        text,
        flags=re.IGNORECASE
    )

    # Remove bullet points and numbering
    text = re.sub(
        r'(?m)^\s*(?:[-–—•*▪◦]+|\d+[.)])\s*',
        '',
        text
    )

    # Split by common separators
    items = re.split(r'[,;+\n|]+', text)

    cleaned_items = []

    for item in items:

        item = re.sub(
            r'^[\s\-–—•*▪◦:]+|[\s\-–—•*▪◦:]+$',
            '',
            item
        ).strip()

        if not item:
            continue

        if item.lower() == "pest control":
            continue

        cleaned_items.append(item)

    return cleaned_items

def insert_food_nutrition_temp(item_name):

    return {
        "serving_size_g": None,
        "calories": None,
        "protein_g": None,
        "carbohydrates_total_g": None,
        "sugar_g": None,
        "fiber_g": None,
        "fat_total_g": None,
        "fat_saturated_g": None,
        "cholesterol_mg": None,
        "sodium_mg": None,
        "potassium_mg": None
    }

@task_routes.post("/get/items_inserted")
def insert_items(db: Session = Depends(get_db)):

    menu_data = get_data()
    # Extract hostel-wise menu data
    menus = extract_items(menu_data, db)
    print(menus)
    inserted_foods = []
    existing_foods = []
    inserted_menus = []
    existing_menus = []
    unmapped_hostels = set()
    # return menus
    try:

        for hostel_menu in menus:

            mess_id = hostel_menu["mess_id"]
            menu_date = hostel_menu["menu_date"]

            if not mess_id:
                unmapped_hostels.add(hostel_menu["Hostel_name"])
                continue

            for meal_type, items in hostel_menu["times"].items():

                # Your database requires uppercase meal types
                meal_type = meal_type.upper()

                for item_name in items:

                    item_name = item_name.strip()

                    if not item_name:
                        continue

                    # 1. Check existing food
                    food = db.query(FoodItem).filter(
                        FoodItem.name.ilike(item_name)
                    ).first()

                    # 2. Insert food if not existing
                    if not food:

                        food_info = insert_food_nutrition(item_name)

                        food = FoodItem(
                            name=item_name,
                            serving_size_g=food_info.get("serving_size_g"),
                            calories=food_info.get("calories"),
                            protein_g=food_info.get("protein_g"),
                            carbohydrates_total_g=food_info.get("carbohydrates_total_g"),
                            sugar_g=food_info.get("sugar_g"),
                            fiber_g=food_info.get("fiber_g"),
                            fat_total_g=food_info.get("fat_total_g"),
                            fat_saturated_g=food_info.get("fat_saturated_g"),
                            cholesterol_mg=food_info.get("cholesterol_mg"),
                            sodium_mg=food_info.get("sodium_mg"),
                            potassium_mg=food_info.get("potassium_mg")
                        )

                        db.add(food)
                        db.flush()

                        inserted_foods.append(item_name)

                    else:
                        existing_foods.append(item_name)

                    # 3. Check whether menu entry already exists
                    existing_menu = db.query(MessMenu).filter(
                        MessMenu.mess_id == mess_id,
                        MessMenu.food_item_id == food.id,
                        MessMenu.menu_date == menu_date,
                        MessMenu.meal_type == meal_type
                    ).first()

                    if existing_menu:
                        existing_menus.append(item_name)
                        continue

                    # 4. Insert into MessMenu
                    mess_menu = MessMenu(
                        mess_id=mess_id,
                        food_item_id=food.id,
                        menu_date=menu_date,
                        meal_type=meal_type,
                        serving_quantity=None,
                        serving_unit=None,
                        source_batch_id=None
                    )

                    db.add(mess_menu)

                    inserted_menus.append({
                        "food_name": item_name,
                        "food_item_id": food.id,
                        "mess_id": mess_id,
                        "menu_date": str(menu_date),
                        "meal_type": meal_type
                    })

        db.commit()

    except IntegrityError as exc:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Duplicate food or mess menu record"
        ) from exc

    except Exception:
        db.rollback()
        raise

    return {
        "message": "Food items and mess menus processed successfully",
        "new_foods_inserted": len(inserted_foods),
        "existing_foods_skipped": len(existing_foods),
        "new_menus_inserted": len(inserted_menus),
        "existing_menus_skipped": len(existing_menus),
        "unmapped_hostels": sorted(unmapped_hostels),
        "inserted_foods": inserted_foods,
        "existing_foods": existing_foods,
        "inserted_menus": inserted_menus
    }

#calling clorie api
def insert_food_nutrition(query):
    API_KEY = os.getenv("CALORIE_NINJA_API_KEY")
    if not API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Nutrition API key is not configured",
        )

    try:
        response = requests.get(
            "https://api.calorieninjas.com/v1/nutrition",
            params={"query": query},
            headers={"X-Api-Key": API_KEY},
            timeout=15,
        )
        response.raise_for_status()
        nutrition_data = response.json()
    except (requests.RequestException, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not retrieve valid nutrition data",
        ) from exc

    if (
        not isinstance(nutrition_data, dict)
        or not isinstance(nutrition_data.get("items"), list)
        or not nutrition_data["items"]
    ):
        return insert_food_nutrition_temp(query)

    return modify_response_ninjas(nutrition_data)


#modifying cloariesapi response
def modify_response_ninjas(obj):

    overall = {}

    for i in obj['items']:
        for j, value in i.items():
            if j != "name":
                overall[j] = overall.get(j, 0) + value
    return overall


def get_data_from_client(query):
    if not isinstance(query, str) or not query.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="A food name is required",
        )

    fields = (
        "serving_size_g",
        "calories",
        "protein_g",
        "carbohydrates_total_g",
        "sugar_g",
        "fiber_g",
        "fat_total_g",
        "fat_saturated_g",
        "cholesterol_mg",
        "sodium_mg",
        "potassium_mg",
    )

    payload = {
        "model": os.getenv("OLLAMA_MODEL", "qwen2.5:7b"),
        "temperature": 0,
        "response_format": {"type": "json_object"},
        "messages": [
            {
                "role": "system",
                "content": (
                    "Estimate nutrition for the named food. Return only a JSON "
                    "object with the requested nutrient keys. Values must be "
                    "non-negative numbers or null. All nutrients must describe "
                    "the same typical serving, whose mass is serving_size_g. "
                    "Use null if a value cannot be estimated. Do not include "
                    "units or extra keys."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Estimate one typical serving of {query.strip()}. "
                    f"Return these exact keys: {', '.join(fields)}."
                ),
            },
        ],
    }

    endpoint = os.getenv(
        "OLLAMA_CHAT_COMPLETIONS_URL",
        "http://localhost:11434/v1/chat/completions",
    )

    try:
        response = requests.post(endpoint, json=payload, timeout=90)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not retrieve nutrition data from Qwen via Ollama",
        ) from exc

    try:
        content = response.json()["choices"][0]["message"]["content"]
        nutrition = json.loads(content)
    except (ValueError, KeyError, IndexError, TypeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Qwen returned an invalid nutrition response",
        ) from exc

    if not isinstance(nutrition, dict) or any(
        field not in nutrition for field in fields
    ):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Qwen response is missing required nutrition fields",
        )

    result = {}
    for field in fields:
        value = nutrition[field]
        if value is None:
            result[field] = None
        elif (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
            or value < 0
        ):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Qwen returned an invalid value for {field}",
            )
        else:
            result[field] = value

    if not result["serving_size_g"]:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Qwen returned an invalid serving size",
        )

    return result


