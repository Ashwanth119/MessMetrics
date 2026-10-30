from fastapi import FastAPI, HTTPException, Query
from openai import OpenAI
import requests
import os

app = FastAPI(title="MessMetrics API")


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

MESS_API_URL = "https://gymkhana.iitb.ac.in/instiapp/api/mess"

CALORIE_API_URL = "https://api.calorieninjas.com/v1/nutrition"

CALORIE_API_KEY = "awJWYcYr4okypbo2qZ8lag==WmaDLqvIbCCxjbWL"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/154.0.0.0 Safari/537.36 Edg/154.0.0.0"
    )
}

MEALS = ["breakfast", "lunch", "snacks", "dinner"]


# --------------------------------------------------
# HOME ROUTE
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "Welcome to MessMetrics API"
    }


# --------------------------------------------------
# FETCH ALL HOSTEL MENUS
# --------------------------------------------------

def fetch_mess_data():

    try:
        response = requests.get(
            MESS_API_URL,
            headers=HEADERS,
            timeout=15
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as e:
        raise HTTPException(
            status_code=502,
            detail=f"Unable to fetch mess data: {str(e)}"
        )


@app.get("/calories")
def get_items():

    data = fetch_mess_data()

    return data


# --------------------------------------------------
# EXTRACT FOOD ITEMS FROM A MEAL
# --------------------------------------------------

def extract_items(menu, meal):

    if meal not in MEALS:
        raise HTTPException(
            status_code=400,
            detail="Invalid meal name"
        )

    meal_data = menu.get(meal, "")

    if not meal_data:
        return []

    items = [
        item.strip()
        for item in meal_data.split(",")
        if item.strip()
    ]

    return items


# --------------------------------------------------
# FETCH NUTRITION INFORMATION
# --------------------------------------------------

def api_request(q: str):

    if not CALORIE_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="CalorieNinjas API key is not configured"
        )

    headers = {
        "X-Api-Key": CALORIE_API_KEY
    }

    params = {
        "query": q
    }

    try:
        response = requests.get(
            CALORIE_API_URL,
            params=params,
            headers=headers,
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        if not data.get("items"):
            return {
                "item": q,
                "status": "Not Found"
            }

        return {
            "item": q,
            "status": "success",
            "nutrition": data["items"]
        }

    except requests.RequestException:
        return {
            "item": q,
            "status": "error",
            "message": "Nutrition API request failed"
        }


# --------------------------------------------------
# GET CALORIES FOR MULTIPLE FOOD ITEMS
# --------------------------------------------------

def calculate_nutrition(items):

    results = []

    for item in items:

        nutrition = api_request(item)

        results.append(nutrition)

    return results


@app.get("/req_cal")
def request_calories(
    item_name: list[str] = Query(...)
):

    results = calculate_nutrition(item_name)

    return {
        "results": results
    }


# --------------------------------------------------
# GET A PARTICULAR HOSTEL'S MENU
# --------------------------------------------------

@app.get("/menu")
def get_menu(
    hostel_name: str = "Hostel 7",
    day: int = 3
):

    data = fetch_mess_data()

    for hostel in data:

        if hostel.get("name") == hostel_name:

            for menu in hostel.get("mess", []):

                if menu.get("day") == day:

                    return {
                        "hostel": hostel_name,
                        "day": day,
                        "menu": menu
                    }

            raise HTTPException(
                status_code=404,
                detail="Day not found"
            )

    raise HTTPException(
        status_code=404,
        detail="Hostel not found"
    )


# --------------------------------------------------
# GET NUTRITION FOR A PARTICULAR MEAL
# --------------------------------------------------

@app.get("/get_calories")
def get_calories(
    hostel_name: str = "Hostel 7",
    day: int = 3,
    meal: str = "breakfast"
):

    if meal not in MEALS:
        raise HTTPException(
            status_code=400,
            detail="Meal must be breakfast, lunch, snacks or dinner"
        )

    data = fetch_mess_data()

    for hostel in data:

        if hostel.get("name") == hostel_name:

            for menu in hostel.get("mess", []):

                if menu.get("day") == day:

                    items = extract_items(menu, meal)

                    if not items:
                        raise HTTPException(
                            status_code=404,
                            detail="No food items found"
                        )

                    nutrition = calculate_nutrition(items)

                    return {
                        "hostel": hostel_name,
                        "day": day,
                        "meal": meal,
                        "food_items": items,
                        "nutrition": nutrition
                    }

            raise HTTPException(
                status_code=404,
                detail="Day not found"
            )

    raise HTTPException(
        status_code=404,
        detail="Hostel not found"
    )


# --------------------------------------------------
# TOTAL CALORIES OF A MEAL
# --------------------------------------------------

@app.get("/total_calories")
def total_calories(
    hostel_name: str = "Hostel 7",
    day: int = 3,
    meal: str = "breakfast"
):

    if meal not in MEALS:
        raise HTTPException(
            status_code=400,
            detail="Invalid meal"
        )

    data = fetch_mess_data()

    for hostel in data:

        if hostel.get("name") == hostel_name:

            for menu in hostel.get("mess", []):

                if menu.get("day") == day:

                    items = extract_items(menu, meal)

                    if not items:
                        raise HTTPException(
                            status_code=404,
                            detail="No food items found"
                        )

                    nutrition_results = calculate_nutrition(items)

                    total = {
                        "calories": 0,
                        "protein_g": 0,
                        "carbohydrates_total_g": 0,
                        "fat_total_g": 0
                    }

                    for result in nutrition_results:

                        if result.get("status") != "success":
                            continue

                        for food in result["nutrition"]:

                            total["calories"] += food.get("calories", 0)
                            total["protein_g"] += food.get("protein_g", 0)
                            total["carbohydrates_total_g"] += food.get(
                                "carbohydrates_total_g", 0
                            )
                            total["fat_total_g"] += food.get(
                                "fat_total_g", 0
                            )

                    return {
                        "hostel": hostel_name,
                        "day": day,
                        "meal": meal,
                        "food_items": items,
                        "total_nutrition": total,
                        "individual_nutrition": nutrition_results
                    }

            raise HTTPException(
                status_code=404,
                detail="Day not found"
            )

    raise HTTPException(
        status_code=404,
        detail="Hostel not found"
    )


# --------------------------------------------------
# LOCAL LLM CLIENT (OPTIONAL)
# --------------------------------------------------

def llm_client(prompt="Hello LLM"):

    client = OpenAI(
        base_url="http://127.0.0.1:11434/v1",
        api_key="dummy_key"
    )

    response = client.chat.completions.create(
        model="qwen3:4b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content