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

class CareerRoleCreate(BaseModel):
    name:  str = Field(min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=500)


class CareerRoleResponse(BaseModel):
    id: int
    name: str
    description: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CareerRoleSkillCreate(BaseModel):
    skill_id: int
    required_level: int = Field(ge=1, le=5)
    importance: str = Field(default="core", max_length=30)
    trend_type: str = Field(default="current", max_length=30)


class CareerRoleSkillResponse(BaseModel):
    id: int
    career_role_id: int
    skill_id: int
    required_level: int
    importance: str
    trend_type: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SkillGapItem(BaseModel):
    skill_id: int
    skill_name: str

    current_level: int
    required_level: int

    gap: int

    importance: str
    trend_type: str


class SkillGapResponse(BaseModel):
    career_id: int
    career_name: str

    skills: list[SkillGapItem]

class CareerRecommendationItem(BaseModel):
    career_id: int
    career_name: str
    match_percentage: int
    requirements_met: int
    total_required_skills: int


class CareerRecommendationResponse(BaseModel):
    recommendations: list[CareerRecommendationItem]

class LearningRoadmapItem(BaseModel):
    skill_id: int
    skill_name: str

    current_level: int
    target_level: int
    gap: int

    priority: int
    suggested_action: str


class LearningRoadmapResponse(BaseModel):
    career_id: int
    career_name: str

    roadmap: list[LearningRoadmapItem]