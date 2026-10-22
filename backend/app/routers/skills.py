from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from .users import get_current_user


router = APIRouter(
    prefix="/skills",
    tags=["Skills"],
)


@router.post(
    "",
    response_model=schemas.SkillResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_skill(
    skill: schemas.SkillCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    skill_name = skill.name.strip()

    existing_skill = db.scalar(
        select(models.Skill).where(
            func.lower(models.Skill.name) == skill_name.lower()
        )
    )

    if existing_skill:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Skill already exists",
        )

    new_skill = models.Skill(
        name=skill_name,
        category=skill.category.strip() if skill.category else None,
    )

    db.add(new_skill)
    db.commit()
    db.refresh(new_skill)

    return new_skill


@router.get(
    "",
    response_model=list[schemas.SkillResponse],
)
def get_skills(
    db: Session = Depends(get_db),
):
    skills = db.scalars(
        select(models.Skill).order_by(models.Skill.name)
    ).all()

    return skills


@router.post(
    "/me",
    response_model=schemas.UserSkillResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_my_skill(
    user_skill: schemas.UserSkillCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    skill = db.get(models.Skill, user_skill.skill_id)

    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found",
        )

    existing_user_skill = db.scalar(
        select(models.UserSkill).where(
            models.UserSkill.user_id == current_user.id,
            models.UserSkill.skill_id == user_skill.skill_id,
        )
    )

    if existing_user_skill:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Skill already added",
        )

    new_user_skill = models.UserSkill(
        user_id=current_user.id,
        skill_id=user_skill.skill_id,
        proficiency_level=user_skill.proficiency_level,
    )

    db.add(new_user_skill)
    db.commit()
    db.refresh(new_user_skill)

    return new_user_skill


@router.get(
    "/me",
    response_model=list[schemas.UserSkillResponse],
)
def get_my_skills(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    user_skills = db.scalars(
        select(models.UserSkill).where(
            models.UserSkill.user_id == current_user.id
        )
    ).all()

    return user_skills

@router.patch(
    "/me/{skill_id}",
    response_model=schemas.UserSkillResponse,
)
def update_my_skill(
    skill_id: int,
    update_data: schemas.UserSkillUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    user_skill = db.scalar(
        select(models.UserSkill).where(
            models.UserSkill.user_id == current_user.id,
            models.UserSkill.skill_id == skill_id,
        )

    )

    if not user_skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User skill not found",
        )

    user_skill.proficiency_level = update_data.proficiency_level

    db.commit()
    db.refresh(user_skill)

    return user_skill

@router.delete(
    "/me/{skill_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_my_skill(
    skill_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    user_skill = db.scalar(
        select(models.UserSkill).where(
            models.UserSkill.user_id == current_user.id,
            models.UserSkill.skill_id == skill_id,
        )
    )

    if not user_skill:
        raise HTTPException(
            
        )