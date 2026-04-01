from fastapi import APIRouter, Depends, Response

from dotenv import load_dotenv
import os

from services.auth_service import AuthService
from services.permissions_service import PermissionsService
from database.postgres_connection import get_postgres_db
from sqlalchemy.orm import Session

from schemas.login_request import LoginRequest
from schemas.register_request import RegisterRequest
from schemas.user_response import user_response


auth_router = APIRouter(tags=["Authentication"])


auth_service = AuthService()
permissions_service = PermissionsService()


@auth_router.post("/login", status_code=200, response_model=user_response)
async def login(
    response: Response,
    login_request: LoginRequest,
    db: Session = Depends(get_postgres_db)
):
    user = auth_service.authenticate(login_request.email, login_request.password, db)

    load_dotenv()
    ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

    token = permissions_service.create_access_token(user.email)
    response.set_cookie(
        key = "access_token",
        value = token,
        httponly = True,
        secure = False,
        samesite = "lax",
        max_age = int(ACCESS_TOKEN_EXPIRE_MINUTES) * 60  # seconds
    )
    return user

@auth_router.post("/register", status_code=201, response_model=user_response)
async def register(register_request: RegisterRequest, db: Session = Depends(get_postgres_db)):
    return auth_service.create_user(register_request, db)

@auth_router.post("/logout", status_code=200)
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Logout successful"}