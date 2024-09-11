from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import List

from src.database import get_db
from src.messages.schemas import MessageReq, MessageResponse, MessageUpdate
from src.messages.service import create_message, get_messages, get_message, update_message, delete_message

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

@router.post("/messages/", response_model=MessageResponse, summary="Create a new message", tags=["Messages"])
@limiter.limit("30/minute")
async def create_message_route(request: Request, message: MessageReq, db: AsyncSession = Depends(get_db)):
    """
    Create a new message with the given text.

    - **message**: Message content provided by the user.
    - **Returns**: Created message with `id` and `text`.

    Example:
    ```
    {
        "text": "Hello World!"
    }
    ```
    """
    return await create_message(db=db, message=message)

@router.get("/messages/", response_model=List[MessageResponse], summary="Retrieve all messages", tags=["Messages"])
@limiter.limit("60/minute")
async def get_messages_route(request: Request, skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    """
    Retrieve a list of all messages.

    - **skip**: Number of items to skip for pagination.
    - **limit**: Maximum number of messages to return.

    Example request:
    ```
    GET /messages?skip=0&limit=10
    ```

    Example response:
    ```
    [
        {
            "id": 1,
            "text": "Hello World!"
        },
        {
            "id": 2,
            "text": "Another message"
        }
    ]
    ```
    """
    return await get_messages(db=db, skip=skip, limit=limit)

@router.get("/messages/{message_id}", response_model=MessageResponse, summary="Get a message by ID", tags=["Messages"])
@limiter.limit("60/minute")
async def get_message_route(request: Request, message_id: int, db: AsyncSession = Depends(get_db)):
    """
    Retrieve a single message by its ID.

    - **message_id**: The ID of the message to retrieve.

    Example request:
    ```
    GET /messages/1
    ```

    Example response:
    ```
    {
        "id": 1,
        "text": "Hello World!"
    }
    ```

    If the message does not exist, a `404 Not Found` error is returned.
    """
    message = await get_message(db=db, message_id=message_id)
    if message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    return message

@router.put("/messages/{message_id}", response_model=MessageResponse, summary="Update a message by ID", tags=["Messages"])
@limiter.limit("15/minute")
async def update_message_route(request: Request, message_id: int, message: MessageUpdate, db: AsyncSession = Depends(get_db)):
    """
    Update an existing message by its ID.

    - **message_id**: The ID of the message to update.
    - **message**: New text for the message.

    Example request:
    ```
    PUT /messages/1
    {
        "text": "Updated message content"
    }
    ```

    If the message does not exist, a `404 Not Found` error is returned.
    """
    updated_message = await update_message(db=db, message_id=message_id, message=message)
    if updated_message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    return updated_message

@router.delete("/messages/{message_id}", response_model=MessageResponse, summary="Delete a message by ID", tags=["Messages"])
@limiter.limit("60/minute")
async def delete_message_route(request: Request, message_id: int, db: AsyncSession = Depends(get_db)):
    """
    Delete a message by its ID.

    - **message_id**: The ID of the message to delete.

    Example request:
    ```
    DELETE /messages/1
    ```

    If the message does not exist, a `404 Not Found` error is returned.
    """
    deleted_message = await delete_message(db=db, message_id=message_id)
    if deleted_message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    return deleted_message
