from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from database import SessionLocal
from model import User
from schemas import (
    UserCreate,
    UserUpdate,
    LoginRequest,
    UserResponse
)
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token
)


app = FastAPI()

security = HTTPBearer()


# =========================
# Database Dependency
# =========================

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# =========================
# JWT Authentication
# =========================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    user_id = verify_token(token)

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    user = db.query(User).filter(
        User.id == int(user_id)
    ).first()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return user


# =========================
# Admin Authorization
# =========================

def get_current_admin(
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    return current_user


# =========================
# Home
# =========================

@app.get("/")
def home():
    return {
        "message": "FastAPI MySQL Learning Project"
    }


# =========================
# Register
# =========================

@app.post("/register", status_code=201)
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    hashed_password = hash_password(user.password)

    new_user = User(
        name=user.name,
        email=user.email,
        password=hashed_password,
        role="user"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "id": new_user.id,
        "name": new_user.name,
        "email": new_user.email,
        "role": new_user.role
    }


# =========================
# Login
# =========================

@app.post("/login")
def login(
    user: LoginRequest,
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    password_correct = verify_password(
        user.password,
        existing_user.password
    )

    if not password_correct:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token({
        "sub": str(existing_user.id),
        "role": existing_user.role
    })

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# =========================
# Get All Users
# =========================

@app.get("/users", response_model=list[UserResponse])
def get_users(
    db: Session = Depends(get_db)
):
    users = db.query(User).all()

    return users


# =========================
# Get Current Logged-in User
# =========================

# IMPORTANT:
# This route must come BEFORE /users/{user_id}

@app.get("/users/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    return current_user


# =========================
# Get One User
# =========================

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


# =========================
# Update User
# =========================

@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(
        User.id == user_id
    ).first()

    if existing_user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    existing_user.name = user.name
    existing_user.email = user.email

    db.commit()
    db.refresh(existing_user)

    return existing_user


# =========================
# Delete User
# =========================

@app.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    db.delete(user)
    db.commit()

    return {
        "message": "User deleted successfully",
        "id": user_id
    }


# =========================
# Admin Dashboard
# =========================

@app.get("/admin")
def admin_dashboard(
    current_user: User = Depends(get_current_admin)
):
    return {
        "message": "Welcome to the admin dashboard",
        "user": current_user.name,
        "role": current_user.role
    }