from pathlib import Path

from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

from src.api import (
    users_router,
    campaigns_router,
    tasks_router,
    rigs_router,
    wells_router,
    dashboard_router,
)
from src.ui.routes import router as ui_router

# For mock implementation, we don't need to create database tables
# from src.database import engine, Base
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Drilling Campaign Management System",
    description="A modern system for managing drilling campaigns, tasks, rigs, and wells",
    version="1.0.0"
)

TEMPLATE_DIR = Path(__file__).resolve().parent / "ui" / "templates"
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))

# Include API routers
app.include_router(users_router)
app.include_router(campaigns_router)
app.include_router(tasks_router)
app.include_router(rigs_router)
app.include_router(wells_router)
app.include_router(dashboard_router)
app.include_router(ui_router, prefix="/ui")


@app.get("/")
async def root():
    return {
        "message": "Welcome to the Drilling Campaign Management System API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
