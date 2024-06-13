# test_router.py
from fastapi import APIRouter, Depends
from master_server.database.user.model import User
from master_server.dependencies.auth import get_current_active_user

app_test_router = APIRouter()


@app_test_router.get("/user/active-user")
async def get_active_user(current_user: User = Depends(get_current_active_user)):
    return current_user
