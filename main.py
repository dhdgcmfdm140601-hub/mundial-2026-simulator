from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import IntegrityError
from database import engine, Base
from routers import users_router, teams_router, players_router, simulator_router, metrics_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mundial 2026 - Simulator API")


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    return JSONResponse(status_code=409, content={"detail": "Resource already exists"})

app.include_router(users_router)
app.include_router(teams_router)
app.include_router(players_router)
app.include_router(simulator_router)
app.include_router(metrics_router)

app.mount("/", StaticFiles(directory="static", html=True), name="static")