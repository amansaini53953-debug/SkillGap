from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from .users import get_current_user


router = APIRouter(
    prefix="/careers",
    tags=["Careers"],
)


@router.post(
    "",
    response_model=schemas.CareerRoleResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_career(
    career: schemas.CareerRoleCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    career_name = career.name.strip()

    existing_career = db.scalar(
        select(models.CareerRole).where(
            func.lower(models.CareerRole.name) == career_name.lower()
        )
    )

    if existing_career:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Career role already exists",
        )

    new_career = models.CareerRole(
        name=career_name,
        description=career.description.strip()
        if career.description
        else None,
    )

    db.add(new_career)
    db.commit()
    db.refresh(new_career)

    return new_career


@router.get(
    "",
    response_model=list[schemas.CareerRoleResponse],
)
def get_careers(
    db: Session = Depends(get_db),
):
    careers = db.scalars(
        select(models.CareerRole).order_by(models.CareerRole.name)
    ).all()

    return careers

@router.post(
    "/{career_id}/skills",
    response_model=schemas.CareerRoleSkillResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_career_skill(
    career_id: int,
    data: schemas.CareerRoleSkillCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    career = db.get(models.CareerRole, career_id)

    if not career:
        raise HTTPException(
            status_code=404,
            detail="Career role not found",
        )

    skill = db.get(models.Skill, data.skill_id)

    if not skill:
        raise HTTPException(
            status_code=404,
            detail="Skill not found",
        )

    existing = db.scalar(
        select(models.CareerRoleSkill).where(
            models.CareerRoleSkill.career_role_id == career_id,
            models.CareerRoleSkill.skill_id == data.skill_id,
        )
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Skill already added to this career",
        )

    new_career_skill = models.CareerRoleSkill(
        career_role_id=career_id,
        skill_id=data.skill_id,
        required_level=data.required_level,
        importance=data.importance,
        trend_type=data.trend_type,
    )

    db.add(new_career_skill)
    db.commit()
    db.refresh(new_career_skill)

    return new_career_skill
@router.get(
    "/{career_id}/skills",
    response_model=list[schemas.CareerRoleSkillResponse],
)
def get_career_skills(
    career_id: int,
    db: Session = Depends(get_db),
):
    career = db.get(models.CareerRole, career_id)

    if not career:
        raise HTTPException(
            status_code=404,
            detail="Career role not found",
        )

    career_skills = db.scalars(
        select(models.CareerRoleSkill).where(
            models.CareerRoleSkill.career_role_id == career_id
        )
    ).all()

    return career_skills

@router.get(
    "/{career_id}/gap",
    response_model=schemas.SkillGapResponse,
)
def get_skill_gap(
    career_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Check whether the career exists
    career = db.get(models.CareerRole, career_id)

    if not career:
        raise HTTPException(
            status_code=404,
            detail="Career role not found",
        )

    # Get required skills and their names
    required_skills = db.execute(
        select(models.CareerRoleSkill, models.Skill.name)
        .join(models.Skill)
        .where(models.CareerRoleSkill.career_role_id == career_id)
    ).all()

    # Get logged-in user's skills
    user_skills = db.scalars(
        select(models.UserSkill).where(
            models.UserSkill.user_id == current_user.id
        )
    ).all()

    # Create skill_id → current_level mapping
    user_levels = {
        skill.skill_id: skill.proficiency_level
        for skill in user_skills
    }

    gap_results = []

    # Compare each required skill
    for required, skill_name in required_skills:

        current_level = user_levels.get(required.skill_id, 0)

        gap = max(required.required_level - current_level, 0)

        gap_results.append({
            "skill_id": required.skill_id,
            "skill_name": skill_name,
            "current_level": current_level,
            "required_level": required.required_level,
            "gap": gap,
            "importance": required.importance,
            "trend_type": required.trend_type,
        })

    return {
        "career_id": career.id,
        "career_name": career.name,
        "skills": gap_results,
    }

@router.get(
    "/recommendations/me",
    response_model=schemas.CareerRecommendationResponse,
)
def recommend_careers(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Get logged-in user's skills
    user_skills = db.scalars(
        select(models.UserSkill).where(
            models.UserSkill.user_id == current_user.id
        )
    ).all()

    user_levels = {
        skill.skill_id: skill.proficiency_level
        for skill in user_skills
    }

    # Get all available careers
    careers = db.scalars(
        select(models.CareerRole)
    ).all()

    recommendations = []

    for career in careers:

        # Get current skill requirements
        required_skills = db.scalars(
            select(models.CareerRoleSkill).where(
                models.CareerRoleSkill.career_role_id == career.id,
                models.CareerRoleSkill.trend_type == "current",
            )
        ).all()

        if not required_skills:
            continue

        total_match = 0
        requirements_met = 0

        for skill in required_skills:
            current_level = user_levels.get(skill.skill_id, 0)
            required_level = skill.required_level

            match = min(current_level / required_level, 1)

            total_match += match

            if current_level >= required_level:
                requirements_met += 1

        match_percentage = round(
            (total_match / len(required_skills)) * 100
        )

        recommendations.append({
            "career_id": career.id,
            "career_name": career.name,
            "match_percentage": match_percentage,
            "requirements_met": requirements_met,
            "total_required_skills": len(required_skills),
        })

    # Highest match first
    recommendations.sort(
        key=lambda career: career["match_percentage"],
        reverse=True,
    )

    return {"recommendations": recommendations}
@router.get(
    "/{career_id}/roadmap",
    response_model=schemas.LearningRoadmapResponse,
)
def get_learning_roadmap(
    career_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Use our existing Skill Gap Analysis
    gap_report = get_skill_gap(
        career_id=career_id,
        db=db,
        current_user=current_user,
    )

    # Select skills that need improvement
    missing_skills = [
        skill for skill in gap_report["skills"]
        if skill["gap"] > 0
        and skill["trend_type"] == "current"
    ]

    # Core skills first, then larger gaps
    missing_skills.sort(
        key=lambda skill: (
            0 if skill["importance"] == "core" else 1,
            -skill["gap"],
        )
    )

    # Learning suggestions
    actions = {
        "python": "Practice advanced Python and build projects.",
        "sql": "Learn SQL joins, queries and database design.",
        "fastapi": "Learn FastAPI and build REST APIs.",
        "git": "Practice Git commands, branches and GitHub.",
        "docker": "Learn Docker containers and deployment.",
        "html": "Practice HTML structure and semantic elements.",
        "css": "Learn responsive design, Flexbox and Grid.",
        "javascript": "Practice JavaScript and DOM manipulation.",
        "react": "Build React components and frontend projects.",
    }

    roadmap = []

    for priority, skill in enumerate(missing_skills, start=1):
        skill_name = skill["skill_name"]

        action = actions.get(
            skill_name.lower(),
            f"Learn {skill_name} and build a practical project.",
        )

        roadmap.append({
            "skill_id": skill["skill_id"],
            "skill_name": skill_name,
            "current_level": skill["current_level"],
            "target_level": skill["required_level"],
            "gap": skill["gap"],
            "priority": priority,
            "suggested_action": action,
        })

    return {
        "career_id": gap_report["career_id"],
        "career_name": gap_report["career_name"],
        "roadmap": roadmap,
    }