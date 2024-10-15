import json

from fastapi import HTTPException, status

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail=json.dumps("Could not validate credentials"),
    headers={"Content-Type": "application/json"}, )

user_already_exist_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail=json.dumps("User already exist"),
    headers={"Content-Type": "application/json"},
)

unhandled_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail=json.dumps("Bad request"),
    headers={"Content-Type": "application/json"},
)
