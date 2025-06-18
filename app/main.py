from fastapi import FastAPI
from routes import router
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.include_router(router)


INTERFACE_URL = os.getenv("INTERFACE_URL")

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