from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from models import PyObjectId

class DriverCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    vehicle_info: Optional[str] = None

class DriverLogin(BaseModel):
    email: EmailStr
    password: str

class DriverResponse(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    email: EmailStr
    created_at: datetime
    vehicle_info: Optional[str]

    class Config:
        populate_by_name = True
        json_encoders = {PyObjectId: str}

class DriverUpdate(BaseModel):
    name: Optional[str] = None
    vehicle_info: Optional[str] = None
