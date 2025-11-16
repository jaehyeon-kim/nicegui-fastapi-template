from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.endpoints import login, users, items
from backend.db import init_db
from frontend import init_frontend


@asynccontextmanager
async def lifespan(backend: FastAPI):
    print("INFO:     Initializing database...")
    init_db.init()
    print("INFO:     Database initialization complete.")
    yield
    print("INFO:     Application shutting down.")


# Pass the lifespan manager to the FastAPI app
app = FastAPI(title="FastAPI NiceGUI Template", lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routers
app.include_router(login.router, tags=["login"])
app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(items.router, prefix="/api/v1", tags=["items"])

# Mount NiceGUI
init_frontend(app)
