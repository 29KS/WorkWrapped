from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import (
    employee, productivity, achievement,
    project, attendance, work_statistics,
    performance, burnout, performance_score,
    auth,personality,wrapped
)

app = FastAPI(title="WorkWrapped API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(employee.router)
app.include_router(productivity.router)
app.include_router(achievement.router)
app.include_router(project.router)
app.include_router(personality.router)
app.include_router(attendance.router)
app.include_router(work_statistics.router)
app.include_router(performance.router)
app.include_router(burnout.router)
app.include_router(performance_score.router)
app.include_router(wrapped.router)


@app.get("/")
async def root():
    return {"message": "WorkWrapped API is running"}