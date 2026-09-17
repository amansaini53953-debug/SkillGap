from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return{"message": "SkillGap API is working"}