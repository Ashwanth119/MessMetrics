from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

from datetime import date, datetime, timezone

from sqlalchemy import select, delete
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import IntegrityError

from app.router1 import task_routes
from app.database import Base, engine, get_db
from app.models import (
    User, Hostel, HostelAdminRequest, Role, UserRole, StudentProfile, Mess, HostelMess,
    FoodItem, MessMenu, MenuUpdateBatch, MenuSourceSnapshot, MenuChangeLog,
    MealLog, MealLogItem
)
from app.schemas import (
    UserCreate, UserUpdate, UserResponse, TokenResponse,
    HostelAdminRegister, StudentRegister,
    MealLogUpsert, MealLogResponse
)
from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    get_current_roles,
    require_role,
)

import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="MessMetrics API",
    lifespan=lifespan,
)


app.include_router(task_routes)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in os.getenv("FRONTEND_ORIGINS", "").split(",")
        if origin.strip()
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Home
@app.get("/")
def home():
    return {"message": "Welcome to MessMetrics API"}


# CREATE: Register a user
@app.post(
    "/auth/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    data: UserCreate,
    db: Session = Depends(get_db),
):
    existing_user = db.scalar(
        select(User).where(
            (User.username == data.username)
            | (User.email == data.email)
        )
    )

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Username or email already registered",
        )

    user = User(
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password),
    )

    db.add(user)

    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Username or email already registered",
        )

    return user


# READ + AUTHENTICATE: Login
@app.post("/auth/login", response_model=TokenResponse)
def login_user(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.scalar(
        select(User).where(
            (User.username == form.username)
            | (User.email == form.username)
        )
    )

    if (
        user is None
        or not verify_password(form.password, user.hashed_password)
        or not user.is_active
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
    }


# READ: Current logged-in user
@app.get("/users/me", response_model=UserResponse)
def read_current_user(
    current_user: User = Depends(get_current_user),
):
    return current_user


# UPDATE: Current logged-in user
@app.patch("/users/me", response_model=UserResponse)
def update_current_user(
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    updates = data.model_dump(exclude_unset=True)

    for field, value in updates.items():
        if value is None:
            raise HTTPException(
                status_code=422,
                detail=f"{field} cannot be null",
            )

    if "username" in updates:
        duplicate = db.scalar(
            select(User).where(
                User.username == updates["username"],
                User.id != current_user.id,
            )
        )
        if duplicate:
            raise HTTPException(
                status_code=409,
                detail="Username already taken",
            )

    if "email" in updates:
        duplicate = db.scalar(
            select(User).where(
                User.email == updates["email"],
                User.id != current_user.id,
            )
        )
        if duplicate:
            raise HTTPException(
                status_code=409,
                detail="Email already registered",
            )

    if "password" in updates:
        updates["hashed_password"] = hash_password(
            updates.pop("password")
        )

    for field, value in updates.items():
        setattr(current_user, field, value)

    try:
        db.commit()
        db.refresh(current_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Username or email already registered",
        )

    return current_user


# DELETE: Current logged-in user
@app.delete(
    "/users/me",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_current_user(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db.delete(current_user)
    db.commit()
    return None


# CREATE: Register hostel admin
@app.post("/auth/register/hostel-admin", status_code=status.HTTP_201_CREATED)
def register_hostel_admin(data: HostelAdminRegister, db: Session = Depends(get_db)):
    if db.scalar(select(User).where((User.username == data.username) | (User.email == data.email))):
        raise HTTPException(status_code=409, detail="Username or email already registered")

    hostel = db.scalar(select(Hostel).where(Hostel.hostel_number == data.hostel_number, Hostel.is_active.is_(True)))
    if not hostel:
        raise HTTPException(status_code=404, detail="Active hostel not found")

    user = User(username=data.username, email=data.email, hashed_password=hash_password(data.password), is_active=False)
    db.add(user)

    try:
        db.flush()
        request = HostelAdminRequest(user_id=user.id, hostel_id=hostel.id, admin_type=data.admin_type.upper(), status="PENDING")
        db.add(request)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Username, email, or request already exists")

    return {"message": "Registration submitted for approval", "status": "PENDING"}


# READ + Authorize: college admin test 
@app.get("/admin/test")
def admin_test(roles: list[str] = Depends(get_current_roles)):
    if "COLLEGE_ADMIN" not in roles:
        raise HTTPException(status_code=403, detail="Access denied")
    return {"roles": roles}


# READ: get the list of hostel admin requests for registrations
@app.get("/admin/hostel-admin-requests")
def get_hostel_admin_requests(
    db: Session = Depends(get_db),
    _: None = Depends(require_role("COLLEGE_ADMIN"))
):
    return db.scalars(
        select(HostelAdminRequest)
        .where(HostelAdminRequest.status == "PENDING")
        .order_by(HostelAdminRequest.created_at)
    ).all()


# POST: approve hostel admin request for registration
@app.post("/admin/hostel-admin-requests/{request_id}/approve")
def approve_hostel_admin_request(
    request_id: int,
    db: Session = Depends(get_db),
    college_admin: User = Depends(get_current_user),
    _: None = Depends(require_role("COLLEGE_ADMIN"))
):
    request = db.get(HostelAdminRequest, request_id)

    if request is None:
        raise HTTPException(status_code=404, detail="Request not found")

    if request.status != "PENDING":
        raise HTTPException(status_code=400, detail="Request is not pending")

    user = db.get(User, request.user_id)
    role = db.scalar(select(Role).where(Role.name == "HOSTEL_ADMIN"))

    if user is None or role is None:
        raise HTTPException(status_code=500, detail="User or HOSTEL_ADMIN role not found")

    existing_assignment = db.scalar(
        select(UserRole).where(
            UserRole.user_id == user.id,
            UserRole.role_id == role.id,
            UserRole.hostel_id == request.hostel_id
        )
    )

    if existing_assignment is not None:
        raise HTTPException(status_code=400, detail="Hostel admin role already assigned")

    user.is_active = True

    db.add(
        UserRole(
            user_id=user.id,
            role_id=role.id,
            hostel_id=request.hostel_id,
            admin_type=request.admin_type,
            assigned_by=college_admin.id
        )
    )

    request.status = "APPROVED"
    request.reviewed_by = college_admin.id
    request.reviewed_at = datetime.now(timezone.utc)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to approve request")

    return {
        "message": "Hostel admin request approved successfully",
        "request_id": request.id,
        "user_id": user.id,
        "hostel_id": request.hostel_id,
        "admin_type": request.admin_type
    }


# POST: reject hostel admin request for registration
@app.post("/admin/hostel-admin-requests/{request_id}/reject")
def reject_hostel_admin_request(
    request_id: int,
    db: Session = Depends(get_db),
    college_admin: User = Depends(get_current_user),
    _: None = Depends(require_role("COLLEGE_ADMIN"))
):
    request = db.get(HostelAdminRequest, request_id)

    if request is None:
        raise HTTPException(status_code=404, detail="Request not found")

    if request.status != "PENDING":
        raise HTTPException(status_code=400, detail="Request is not pending")

    request.status = "REJECTED"
    request.reviewed_by = college_admin.id
    request.reviewed_at = datetime.now(timezone.utc)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to reject request")

    return {
        "message": "Hostel admin request rejected successfully",
        "request_id": request.id,
        "status": request.status
    }


@app.post("/auth/register/student", status_code=201)
def register_student(
    data: StudentRegister,
    db: Session = Depends(get_db)
):
    existing_user = db.scalar(
        select(User).where(
            (User.username == data.username) |
            (User.email == data.email)
        )
    )

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Username or email already registered"
        )

    existing_roll_number = db.scalar(
        select(StudentProfile).where(
            StudentProfile.roll_number == data.roll_number
        )
    )

    if existing_roll_number:
        raise HTTPException(
            status_code=409,
            detail="Roll number already registered"
        )

    hostel_number = data.hostel_number.upper()

    hostel = db.scalar(
        select(Hostel).where(
            Hostel.hostel_number == hostel_number,
            Hostel.is_active.is_(True)
        )
    )

    if hostel is None:
        raise HTTPException(
            status_code=400,
            detail="Invalid or inactive hostel"
        )

    student_role = db.scalar(
        select(Role).where(Role.name == "STUDENT")
    )

    if student_role is None:
        raise HTTPException(
            status_code=500,
            detail="STUDENT role not configured"
        )

    user = User(
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password),
        is_active=True
    )

    try:
        db.add(user)
        db.flush()

        student_profile = StudentProfile(
            user_id=user.id,
            full_name=data.full_name,
            roll_number=data.roll_number,
            hostel_id=hostel.id,
            room_number=data.room_number,
            date_of_birth=data.date_of_birth,
            height_cm=data.height_cm,
            weight_kg=data.weight_kg,
            activity_level=data.activity_level
        )

        db.add(student_profile)

        user_role = UserRole(
            user_id=user.id,
            role_id=student_role.id,
            hostel_id=hostel.id
        )

        db.add(user_role)
        db.commit()
        db.refresh(user)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Username, email, or roll number already registered"
        )

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Student registration failed"
        )

    return {
        "message": "Student registered successfully",
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": data.full_name,
        "roll_number": data.roll_number,
        "hostel_number": hostel.hostel_number,
        "role": "STUDENT"
    }


@app.get("/hostels")
def get_hostels(db: Session = Depends(get_db)):
    hostels = db.scalars(
        select(Hostel)
        .where(Hostel.is_active.is_(True))
    ).all()

    hostels = sorted(
        hostels,
        key=lambda hostel: int(hostel.hostel_number[1:])
    )

    return [
        {
            "id": hostel.id,
            "hostel_number": hostel.hostel_number,
            "name": hostel.name
        }
        for hostel in hostels
    ]


def get_student_mess(db: Session, user_id: int):
    student = db.scalar(
        select(StudentProfile).where(StudentProfile.user_id == user_id)
    )

    if student is None:
        raise HTTPException(status_code=404, detail="Student profile not found")

    hostel = db.get(Hostel, student.hostel_id)

    if hostel is None:
        raise HTTPException(status_code=404, detail="Hostel not found")

    hostel_mess = db.scalar(
        select(HostelMess).where(HostelMess.hostel_id == hostel.id)
    )

    if hostel_mess is None:
        raise HTTPException(status_code=404, detail="No mess assigned to this hostel")

    mess = db.get(Mess, hostel_mess.mess_id)

    if mess is None or not mess.is_active:
        raise HTTPException(status_code=404, detail="Assigned mess is unavailable")

    return student, hostel, mess


@app.get("/students/me/mess")
def get_my_mess(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    student, hostel, mess = get_student_mess(db, current_user.id)

    return {
        "hostel": {
            "id": hostel.id,
            "hostel_number": hostel.hostel_number,
            "name": hostel.name,
        },
        "mess": {
            "id": mess.id,
            "name": mess.name,
        },
    }


@app.get("/students/me/menu")
def get_my_mess_menu(
    menu_date: date | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    student, hostel, mess = get_student_mess(db, current_user.id)

    target_date = menu_date or date.today()

    menu_items = db.scalars(
        select(MessMenu)
        .where(
            MessMenu.mess_id == mess.id,
            MessMenu.menu_date == target_date,
        )
        .options(selectinload(MessMenu.food_item))
    ).all()

    meal_order = ["BREAKFAST", "LUNCH", "SNACKS", "DINNER"]

    meals = {
        meal: [] for meal in meal_order
    }

    for item in menu_items:
        food = item.food_item

        if food is None or not food.is_active:
            continue

        meals[item.meal_type].append({
            "menu_id": item.id,
            "food_item_id": food.id,
            "name": food.name,
            "serving_quantity": item.serving_quantity,
            "serving_unit": item.serving_unit,
            "nutrition": {
                "serving_size_g": food.serving_size_g,
                "calories": food.calories,
                "protein_g": food.protein_g,
                "carbohydrates_total_g": food.carbohydrates_total_g,
                "sugar_g": food.sugar_g,
                "fiber_g": food.fiber_g,
                "fat_total_g": food.fat_total_g,
                "fat_saturated_g": food.fat_saturated_g,
                "cholesterol_mg": food.cholesterol_mg,
                "sodium_mg": food.sodium_mg,
                "potassium_mg": food.potassium_mg,
            },
        })

    return {
        "menu_date": target_date,
        "hostel": hostel.hostel_number,
        "mess": mess.name,
        "meals": [
            {
                "meal_type": meal,
                "items": meals[meal],
            }
            for meal in meal_order
        ],
    }


@app.put("/students/me/meal-logs", response_model=MealLogResponse)
def save_meal_log(
    data: MealLogUpsert,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    student, hostel, mess = get_student_mess(db, current_user.id)

    menu_ids = [item.mess_menu_id for item in data.items]

    if len(menu_ids) != len(set(menu_ids)):
        raise HTTPException(
            status_code=400,
            detail="Duplicate menu items are not allowed"
        )

    menu_items = db.scalars(
        select(MessMenu)
        .where(
            MessMenu.id.in_(menu_ids),
            MessMenu.mess_id == mess.id,
            MessMenu.menu_date == data.log_date,
            MessMenu.meal_type == data.meal_type,
        )
        .options(selectinload(MessMenu.food_item))
    ).all() if menu_ids else []

    if len(menu_items) != len(menu_ids):
        raise HTTPException(
            status_code=400,
            detail="One or more selected items do not belong to your assigned mess, date, or meal"
        )

    for menu_item in menu_items:
        if menu_item.food_item is None or not menu_item.food_item.is_active:
            raise HTTPException(
                status_code=400,
                detail="One or more selected food items are unavailable"
            )

    meal_log = db.scalar(
        select(MealLog)
        .where(
            MealLog.student_profile_id == student.id,
            MealLog.log_date == data.log_date,
            MealLog.meal_type == data.meal_type,
        )
        .options(selectinload(MealLog.items))
    )

    if meal_log is None:
        meal_log = MealLog(
            student_profile_id=student.id,
            log_date=data.log_date,
            meal_type=data.meal_type
        )
        db.add(meal_log)
        db.flush()

    else:
        db.execute(
            delete(MealLogItem).where(
                MealLogItem.meal_log_id == meal_log.id
            ),
            execution_options={"synchronize_session": False}
        )
        db.flush()
        db.expire(meal_log, ["items"])

    for menu_item in menu_items:
        food = menu_item.food_item

        meal_log.items.append(
            MealLogItem(
                mess_menu_id=menu_item.id,
                food_name=food.name,
                servings_consumed=next(
                    item.servings_consumed
                    for item in data.items
                    if item.mess_menu_id == menu_item.id
                ),
                calories=food.calories,
                protein_g=food.protein_g,
                carbohydrates_total_g=food.carbohydrates_total_g,
                sugar_g=food.sugar_g,
                fiber_g=food.fiber_g,
                fat_total_g=food.fat_total_g,
                fat_saturated_g=food.fat_saturated_g,
                cholesterol_mg=food.cholesterol_mg,
                sodium_mg=food.sodium_mg,
                potassium_mg=food.potassium_mg,
            )
        )

    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        print("MEAL LOG ERROR:", repr(exc), flush=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to save meal log"
        ) from exc

    return db.scalar(
        select(MealLog)
        .where(MealLog.id == meal_log.id)
        .options(selectinload(MealLog.items))
    )


@app.get("/students/me/meal-logs", response_model=list[MealLogResponse])
def get_my_meal_logs(
    log_date: date = date.today(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    student = db.scalar(
        select(StudentProfile)
        .where(StudentProfile.user_id == current_user.id)
    )

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    meal_logs = db.scalars(
        select(MealLog)
        .where(
            MealLog.student_profile_id == student.id,
            MealLog.log_date == log_date
        )
        .options(selectinload(MealLog.items))
        .order_by(MealLog.id)
    ).all()

    return meal_logs


@app.get("/students/me/calories")
def get_my_daily_calories(
    log_date: date = date.today(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    student = db.scalar(
        select(StudentProfile)
        .where(StudentProfile.user_id == current_user.id)
    )

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    meal_logs = db.scalars(
        select(MealLog)
        .where(
            MealLog.student_profile_id == student.id,
            MealLog.log_date == log_date
        )
        .options(selectinload(MealLog.items))
    ).all()

    nutrients = [
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
    ]

    totals = {key: 0.0 for key in nutrients}
    meal_totals = {}

    for meal_log in meal_logs:
        meal_total = {key: 0.0 for key in nutrients}

        for item in meal_log.items:
            for key in nutrients:
                value = getattr(item, key)

                if value is not None:
                    meal_total[key] += value * item.servings_consumed

        meal_totals[meal_log.meal_type] = meal_total

        for key in nutrients:
            totals[key] += meal_total[key]

    return {
        "log_date": log_date,
        "daily_totals": totals,
        "meal_totals": meal_totals,
    }


