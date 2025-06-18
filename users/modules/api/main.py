from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from modules.api.users.routes import users_router
from modules.api.auth.routes import auth_router

import os
from dotenv import load_dotenv

load_dotenv()

INTERFACE_URL = os.getenv("INTERFACE_URL")

def create_app() -> FastAPI:
    app = FastAPI(
    title="Admin Dashboard API",
    description="API de gestion de la base de donnée utilisateur",
    version="1.2.0"
    )

    # Ajout du middleware CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            INTERFACE_URL,
            "http://localhost:8081",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    router = APIRouter()
    router.include_router(auth_router, prefix="/auth", tags=["Authentification"])
    router.include_router(users_router, prefix="/users", tags=["Users"])

    app.include_router(router)

    @app.get("/", include_in_schema=False)
    async def root():
        return RedirectResponse(url="/docs")

    return app