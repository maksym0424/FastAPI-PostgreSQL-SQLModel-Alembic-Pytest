from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .routers import auth_router, user_router
from .config import get_settings
from .config import Environment


# Context manager that will run before the server starts and after the server stops
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run things before the server starts

    # Important to yield after running things before the server starts
    yield

    # Run things before the server stops


# Create the FastAPI app
app = FastAPI()

# Get the settings
app_settings = get_settings()

# Add the CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=app_settings.ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set production settings
if app_settings.ENVIRONMENT == Environment.PRODUCTION.value:
    app.openapi_url = None
    app.docs_url = None
    app.redoc_url = None
    app.debug = False

# Set development settings
elif app_settings.ENVIRONMENT == Environment.DEVELOPMENT.value:
    app.debug = True


# Route handlers


# Index route
@app.get("/")
async def index():
    return {"message": "Master Server API"}


app.include_router(auth_router)
app.include_router(user_router)
