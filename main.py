from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import models, schemas, utils
from database import SessionLocal, engine
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware  # Import CORSMiddleware

app = FastAPI()

# CORS setup to allow requests from your frontend (this part is now removed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for development (modify for production)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

# Create tables if they don't exist
models.Base.metadata.create_all(bind=engine)

# OAuth2 token URL
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register/", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    try:
        hashed_password = utils.hash_password(user.password)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error hashing password: {str(e)}")
    
    new_user = models.User(
        name=user.name,
        age=user.age,
        gender=user.gender,
        email=user.email,
        city=user.city,
        interests=user.interests,
        password=hashed_password
    )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        db.rollback()  # Ensure the transaction is rolled back if any error occurs
        raise HTTPException(status_code=500, detail=f"Error inserting user into database: {str(e)}")
    
    return new_user


@app.post("/login/")
def login_user(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user is None or not utils.verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = utils.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.User)
def read_users_me(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    email = utils.verify_token(token)["sub"]
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

@app.get("/users/{user_id}/matches/", response_model=List[schemas.User])
def find_matches(user_id: int, db: Session = Depends(get_db)):
    current_user = db.query(models.User).filter(models.User.id == user_id).first()
    if current_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    all_users = db.query(models.User).filter(models.User.id != user_id).all()
    matches = []
    for user in all_users:
        if user.city == current_user.city:
            if any(interest in current_user.interests for interest in user.interests):
                matches.append(user)
    
    return matches

@app.get("/users/", response_model=List[schemas.User])
def get_all_users(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    # Verify the token (you can add logic to ensure only admin can access this endpoint)
    utils.verify_token(token)
    
    users = db.query(models.User).all()
    
    if not users:
        raise HTTPException(status_code=404, detail="No users found")
    
    return users

@app.put("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update user details
    if user.name:
        db_user.name = user.name
    if user.age:
        db_user.age = user.age
    if user.gender:
        db_user.gender = user.gender
    if user.email:
        db_user.email = user.email
    if user.city:
        db_user.city = user.city
    if user.interests:
        db_user.interests = user.interests
    if user.password:
        db_user.password = utils.hash_password(user.password)  # If password is updated

    db.commit()
    db.refresh(db_user)  # Refresh the user object with updated data

    return db_user
@app.put("/profile", response_model=schemas.User)
def update_profile(user_data: schemas.UserCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    # Decode token to get the user email
    email = utils.verify_token(token)["sub"]
    db_user = db.query(models.User).filter(models.User.email == email).first()
    
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update user profile details
    if user_data.name:
        db_user.name = user_data.name
    if user_data.age:
        db_user.age = user_data.age
    if user_data.gender:
        db_user.gender = user_data.gender
    if user_data.city:
        db_user.city = user_data.city
    if user_data.interests:
        db_user.interests = user_data.interests
    
    # Password change logic is optional, only if provided
    if user_data.password:
        db_user.password = utils.hash_password(user_data.password)  # If password is updated

    db.commit()
    db.refresh(db_user)  # Refresh the user object with updated data

    return db_user

@app.delete("/users/{user_id}", response_model=schemas.User)
def delete_user(user_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    # Verify the token (you can add logic to ensure only admins can delete users)
    utils.verify_token(token)

    # Get the user by ID
    db_user = db.query(models.User).filter(models.User.id == user_id).first()

    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Delete the user from the database
    db.delete(db_user)
    db.commit()

    return db_user
