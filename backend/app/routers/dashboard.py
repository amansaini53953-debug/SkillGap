from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from .users import get_current_user
from .careers import recommend_careers, get_learning_roadmap


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get(
    "/me",
    response_model=schemas.DashboardResponse,
)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):

    # Count user's skills
    total_skills = db.scalar(
        select(func.count())
        .select_from(models.UserSkill)
        .where(models.UserSkill.user_id == current_user.id)
    )

    # Count available careers
    available_careers = db.scalar(
        select(func.count()).select_from(models.CareerRole)
    )

    top_career = None
    career_match = None
    next_learning_action = None

    # Get career recommendations
    if total_skills > 0:
        result = recommend_careers(
            db=db,
            current_user=current_user,
        )

        recommendations = result["recommendations"]

        if recommendations:
            best = recommendations[0]

            if best["match_percentage"] > 0:
                top_career = best["career_name"]
                career_match = best["match_percentage"]

                # Get first learning action
                roadmap = get_learning_roadmap(
                    career_id=best["career_id"],
                    db=db,
                    current_user=current_user,
                )

                if roadmap["roadmap"]:
                    next_learning_action = (
                        roadmap["roadmap"][0]["suggested_action"]
                    )

    return {
        "user_name": current_user.full_name,
        "total_skills": total_skills,
        "available_careers": available_careers,
        "top_career": top_career,
        "career_match": career_match,
        "next_learning_action": next_learning_action,
    }