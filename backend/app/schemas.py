from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class UserCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=120)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class SkillCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    category: str | None = Field(default=None, max_length=100)

class SkillResponse(BaseModel):
    id: int
    name: str
    category: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserSkillCreate(BaseModel):
    skill_id: int
    proficiency_level: int = Field(ge=1, le=5)


class UserSkillResponse(BaseModel):
    id: int
    user_id: int
    skill_id: int
    proficiency_level: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserSkillUpdate(BaseModel):
    proficiency_level: int = Field(ge=1, le=5)