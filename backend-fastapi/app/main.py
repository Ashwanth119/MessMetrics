
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import (
    User, Hostel, HostelAdminRequest, Role, UserRole, StudentProfile, Mess, HostelMess,
    FoodItem, MessMenu, MenuUpdateBatch, MenuSourceSnapshot, MenuChangeLog,
)
from app.schemas import UserCreate, UserUpdate, UserResponse, TokenResponse, HostelAdminRegister, StudentRegister
from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    get_current_roles,
    require_role,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="MessMetrics API",
    lifespan=lifespan,
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
        raise HTTPException(status_code=409, detail="Roll number already registered")

    hostel_number = data.hostel_number.upper()
    hostel = db.scalar(
        select(Hostel).where(
            Hostel.hostel_number == hostel_number,
            Hostel.is_active.is_(True)
        )
    )

    if hostel is None:
        raise HTTPException(status_code=400, detail="Invalid or inactive hostel")

    student_role = db.scalar(
        select(Role).where(Role.name == "STUDENT")
    )

    if student_role is None:
        raise HTTPException(status_code=500, detail="STUDENT role not configured")

    user = User(
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password),
        is_active=True
    )

    try:
        db.add(user)
        db.flush()

        db.add(
            StudentProfile(
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
        )

        db.add(
            UserRole(
                user_id=user.id,
                role_id=student_role.id,
                hostel_id=hostel.id
            )
        )

        db.commit()
        db.refresh(user)

    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Student registration failed")

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


