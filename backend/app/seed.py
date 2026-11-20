from sqlalchemy import select, func

from . import models
from .database import Base, engine, SessionLocal

skills_data = [
    ("Python", "Programming"),
    ("SQL", "Database"),
    ("FastAPI", "Backend"),
    ("React", "Frontend"),
    ("Git", "Version Control"),
    ("Docker", "DevOps"),
    ("HTML", "Frontend"),
    ("CSS", "Frontend"),
    ("JavaScript", "Programming"),
        ("TypeScript", "Programming"),
    ("Node.js", "Backend"),
    ("Next.js", "Frontend"),
    ("OOP", "Programming"),
    ("REST API", "Backend"),
    ("Excel", "Data Analytics"),
    ("Power BI", "Data Analytics"),
    ("Statistics", "Mathematics"),
    ("NumPy", "Data Science"),
    ("Pandas", "Data Science"),
    ("Machine Learning", "Artificial Intelligence"),
    ("Linux", "Operating System"),
    ("AWS", "Cloud Computing"),
    ("Networking", "Computer Networks"),
    ("CI/CD", "DevOps"),
    ("Kubernetes", "DevOps"),
    ("Terraform", "Cloud Computing"),
    ("Cloud Security", "Cybersecurity"),
    ("Generative AI", "Artificial Intelligence"),
    ("LLMs", "Artificial Intelligence"),
    ("AI Agents", "Artificial Intelligence"),
    ("AI Integration", "Artificial Intelligence"),
    ("GitOps", "DevOps"),
    ("DevSecOps", "DevOps"),

]

careers_data = [
    ("Backend Developer", "Builds server-side applications and APIs."),
    ("Frontend Developer", "Builds interactive and responsive user interfaces."),
    ("Full Stack Developer", "Develops frontend and backend applications."),
    ("Python Developer", "Develops applications using Python."),
    ("Data Analyst", "Analyzes data and generates business insights."),
    ("AI/ML Engineer", "Develops artificial intelligence and machine learning systems."),
    ("Cloud Engineer", "Manages cloud infrastructure and service."),
    ("DevOps Engineer", "Automates software development and deployment."),

]

career_skills_data = {
     "Backend Developer":[
          ("Python", 4, "core", "current"),
          ("SQL", 3, "core", "current"),
          ("FastAPI", 3, "core", "current"),
          ("Git", 3, "important", "current"),
          ("Docker", 2, "important", "current"),
     ],

     "Frontend Developer":[
          ("HTML", 4, "core", "current"),
          ("CSS", 4, "core", "current"),
          ("JavaScript", 4, "core", "current"),
          ("React", 4, "core", "current"),
          ("Git", 3, "important", "current"),
     ],

         "Full Stack Developer": [
        ("HTML", 3, "core", "current"),
        ("CSS", 3, "core", "current"),
        ("JavaScript", 4, "core", "current"),
        ("React", 3, "core", "current"),
        ("Node.js", 3, "core", "current"),
        ("SQL", 3, "important", "current"),
    ],

    "Python Developer": [
        ("Python", 4, "core", "current"),
        ("OOP", 3, "core", "current"),
        ("SQL", 3, "important", "current"),
        ("Git", 3, "important", "current"),
    ],

    "Data Analyst": [
        ("SQL", 4, "core", "current"),
        ("Excel", 4, "core", "current"),
        ("Python", 3, "core", "current"),
        ("Power BI", 3, "important", "current"),
        ("Pandas", 3, "important", "current"),
    ],

    "AI/ML Engineer": [
        ("Python", 4, "core", "current"),
        ("Machine Learning", 4, "core", "current"),
        ("NumPy", 3, "core", "current"),
        ("Pandas", 3, "core", "current"),
        ("Statistics", 3, "important", "current"),
        ("Generative AI", 2, "important", "future"),
    ],

    "Cloud Engineer": [
        ("Linux", 3, "core", "current"),
        ("AWS", 4, "core", "current"),
        ("Networking", 3, "core", "current"),
        ("Docker", 3, "important", "current"),
    ],

    "DevOps Engineer": [
        ("Linux", 4, "core", "current"),
        ("Git", 3, "core", "current"),
        ("Docker", 4, "core", "current"),
        ("CI/CD", 3, "core", "current"),
        ("Kubernetes", 3, "important", "current"),
    ],
}

def seed_database():
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        #skills seeding
        for name, category in skills_data:

            existing = db.scalar(
                select(models.Skill).where(
                    func.lower(models.Skill.name) == name.lower()
                )
            )

            if existing:
                print(f"Already exists: {name}")
                continue

            skill = models.Skill(
                name=name,
                category=category,
            )

            db.add(skill)
            print(f"Adding: {name}")

        #career roles seeding
        for name, description in careers_data:

                existing = db.scalar(
                    select(models.CareerRole).where(
                        func.lower(models.CareerRole.name) == name.lower()
                    )
                )

                if existing:
                    print(f"Career already exists: {name}")
                    continue

                career = models.CareerRole(
                    name=name,
                    description=description,
                )

                db.add(career)
                print(f"Adding career: {name}")

        db.flush()

        #career skills seeding
        for career_name, requirements in career_skills_data.items():

                     career = db.scalar(
                          select(models.CareerRole).where(
                               func.lower(models.CareerRole.name) == career_name.lower()
                            
                          )
                     )

                     if not career:
                          raise ValueError(f"Career not found: {career_name}")

                     for skill_name, level, importance, trend in requirements:

                          skill = db.scalar(
                               select(models.Skill).where(
                                    func.lower(models.Skill.name) == skill_name.lower()
                               )
                          )

                          if not skill:
                               raise ValueError(f"skill not found: {skill_name}")

                          existing = db.scalar(
                               select(models.CareerRoleSkill).where(
                                    models.CareerRoleSkill.career_role_id == career.id,
                                    models.CareerRoleSkill.skill_id == skill.id,
                               )
                          )

                          if existing:
                               print(f"Mapping already exists: {career_name} - {skill_name}")
                               continue

                          mapping = models.CareerRoleSkill(
                               career_role_id=career.id,
                               skill_id=skill.id,
                               required_level=level,
                               importance=importance,
                               trend_type=trend,
                          )

                          db.add(mapping)

                          print(f"Connecting: {career_name} - {skill_name}")
        db.commit()

    print("Database seeding completed successfully.")


if __name__ == "__main__":
    seed_database()