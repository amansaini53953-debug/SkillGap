from fastapi import FastAPI

from . import models
from .database import Base, engine
from .routers import users


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SkillGap API",
    description="Backend API for SkillGap",
    version="1.0.0",
)

app.include_router(users.router)


@app.get("/", tags=["Home"])
def home():
    return {"message": "SkillGap API is working"}