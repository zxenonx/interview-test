from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import Annotated

from app.db.database import get_db
from app.utils import jwt_helpers
from app.core.dependencies.security import get_current_user

from app.api.v1.auth import schemas
from app.api.services.user import UserService
from app.api.models.user import User

auth = APIRouter(prefix="/auth", tags=["Authentication"])


@auth.post(
    path="/register",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.AuthResponse,
    summary="Create a new user account",
    description="This endpoint takes in the user creation details and returns jwt tokens along with user data",
    tags=["Authentication"],
)
def register(
    schema: schemas.RegisterRequest,
    db: Annotated[Session, Depends(get_db)],
):
    """Endpoint for a user to register their account

    Args:
    schema (schemas.LoginRequest): Login request schema
    db (Annotated[Session, Depends): Database session
    """

    # Create user account

    service = UserService(db=db)

    user = service.register(db=db, schema=schema)

    # Create access and refresh tokens
    access_token = jwt_helpers.create_jwt_token("access", user.id)
    refresh_token = jwt_helpers.create_jwt_token("refresh", user.id)

    response_data = schemas.AuthResponseData(
        id=user.id, username=user.username, email=user.email
    )

    return schemas.AuthResponse(
        status_code=status.HTTP_201_CREATED,
        message="User registered successfully",
        access_token=access_token,
        refresh_token=refresh_token,
        data=response_data,
    )


@auth.post(
    path="/login",
    status_code=status.HTTP_200_OK,
    response_model=schemas.AuthResponse,
    summary="Login a registered user",
    description="This endpoint retrieves the jwt tokens for a registered user",
    tags=["Authentication"],
)
def login(
    schema: schemas.LoginRequest,
    db: Annotated[Session, Depends(get_db)],
):
    """Endpoint for user login

    Args:
        schema (schemas.LoginRequest): Login request schema
        db (Annotated[Session, Depends): Database session
    """

    service = UserService(db=db)

    user = service.authenticate(db=db, schema=schema)

    # Create access and refresh tokens
    access_token = jwt_helpers.create_jwt_token("access", user.id)
    refresh_token = jwt_helpers.create_jwt_token("refresh", user.id)

    response_data = schemas.AuthResponseData(
        id=user.id, username=user.username, email=user.email
    )

    return schemas.AuthResponse(
        status_code=status.HTTP_201_CREATED,
        message="User logged in successfully",
        access_token=access_token,
        refresh_token=refresh_token,
        data=response_data,
    )


@auth.post(
    path="/token/refresh",
    response_model=schemas.TokenRefreshResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh tokens",
    description="This endpoint uses the current refresh token to create new access and refresh tokens",
    tags=["Authentication"],
)
def refresh_token(schema: schemas.TokenRefreshRequest):
    """Endpoint to refresh the access token

    Args:
        schema (schemas.TokenRefreshRequest): Refresh Token Schema

    Returns:
        _type_: Refresh Token Response
    """
    token = jwt_helpers.refresh_access_token(refresh_token=schema.refresh_token)

    return schemas.TokenRefreshResponse(
        status_code=status.HTTP_200_OK,
        message="Access token refreshed successfully",
        access_token=token,
    )


@auth.get(
    path="/user",
    response_model=schemas.UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user details",
    description="This endpoint retrieves the details of the logged-in user",
    tags=["Authentication"],
)
def get_user(current_user: Annotated[User, Depends(get_current_user)]):
    user_schema = schemas.AuthResponseData(
        id=current_user.id, username=current_user.username, email=current_user.email
    )

    return schemas.UserResponse(
        status_code=status.HTTP_200_OK,
        message="User Details Retrieved",
        data=user_schema,
    )
