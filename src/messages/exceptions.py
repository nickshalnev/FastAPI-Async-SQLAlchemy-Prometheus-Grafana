import json

from fastapi import HTTPException, status

message_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail=json.dumps("Message not found"),
    headers={"Content-Type": "application/json"},
)

unhandled_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail=json.dumps("Bad request"),
    headers={"Content-Type": "application/json"},
)