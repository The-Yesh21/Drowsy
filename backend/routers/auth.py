from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from bson import ObjectId

from database import get_database
from models.driver import DriverCreate, DriverResponse
from config import settings

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm="HS256")
    return encoded_jwt

async def get_current_driver(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    db = get_database()
    driver = await db.drivers.find_one({"email": email})
    if driver is None:
        raise credentials_exception
    return driver

@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(driver: DriverCreate):
    db = get_database()
    
    if await db.drivers.find_one({"email": driver.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
        
    driver_dict = driver.model_dump()
    driver_dict["hashed_password"] = get_password_hash(driver_dict.pop("password"))
    driver_dict["created_at"] = datetime.utcnow()
    
    result = await db.drivers.insert_one(driver_dict)
    
    access_token = create_access_token(data={"sub": driver.email, "id": str(result.inserted_id)})
    return {"access_token": access_token, "token_type": "bearer", "driver_id": str(result.inserted_id)}

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db = get_database()
    driver = await db.drivers.find_one({"email": form_data.username})
    
    if not driver or not verify_password(form_data.password, driver["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token = create_access_token(data={"sub": driver["email"], "id": str(driver["_id"])})
    return {"access_token": access_token, "token_type": "bearer", "driver_id": str(driver["_id"])}

@router.get("/me", response_model=DriverResponse)
async def read_users_me(current_driver: dict = Depends(get_current_driver)):
    return current_driver
