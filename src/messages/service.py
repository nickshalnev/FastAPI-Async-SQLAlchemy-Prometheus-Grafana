from fastapi import HTTPException
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.messages.exceptions import message_not_found_exception, unhandled_exception
from src.messages.models import Message
from src.messages.schemas import MessageReq, MessageUpdate
from src.config import logger


async def create_message(db: AsyncSession, message: MessageReq):
    try:
        db_message = Message(text=message.text)
        db.add(db_message)
        await db.commit()
        await db.refresh(db_message)
        logger.info(f"Message created with ID {db_message.id}")
        return db_message
    except Exception as e:
        logger.error(f"Unhandled exception: {e.__class__.__name__}\nreturning 400")
        logger.error(f"Database error occurred while creating message")
        raise unhandled_exception


async def get_messages(db: AsyncSession, skip: int = 0, limit: int = 10):
    try:
        result = await db.execute(select(Message).offset(skip).limit(limit))
        messages = result.scalars().all()
        logger.info(f"Retrieved {len(messages)} messages")
        return messages

    except Exception as e:
        logger.error(f"Unhandled exception: {e.__class__.__name__}\nreturning 400")
        logger.error(f"Database error occurred while getting messages")
        raise unhandled_exception


async def get_message(db: AsyncSession, message_id: int):
    try:
        result = await db.execute(select(Message).filter(Message.id == message_id).limit(1))
        message = result.scalars().first()
        if message is None:
            logger.warning(f"Message with ID {message_id} not found")
            raise message_not_found_exception
        logger.info(f"Message with ID {message_id} retrieved")
        return message
    except HTTPException:
        logger.warning(f"Message with ID {message_id} not found for update")
        raise message_not_found_exception
    except Exception as e:
        logger.error(f"Unhandled exception: {e.__class__.__name__}\nreturning 400")
        logger.error(f"Database error occurred while getting message with ID {message_id}: {str(e)}")
        raise unhandled_exception


async def update_message(db: AsyncSession, message_id: int, message: MessageUpdate):
    try:
        stmt = (
            update(Message)
            .where(Message.id == message_id)
            .values(text=message.text)
            .returning(Message)
        )
        try:
            result = await db.execute(stmt)
        except HTTPException:
            logger.warning(f"Message with ID {message_id} not found for update")
            raise message_not_found_exception

        updated_message = result.scalars().first()

        await db.commit()
        logger.info(f"Message with ID {message_id} updated")
        return updated_message

    except Exception as e:
        logger.error(f"Unhandled exception: {e.__class__.__name__}\nreturning 400")
        logger.error(f"Database error occurred while updating message with ID {message_id}: {str(e)}")
        raise unhandled_exception


async def delete_message(db: AsyncSession, message_id: int):
    try:
        result = await db.execute(select(Message).filter(Message.id == message_id))
        db_message = result.scalars().first()
        if not db_message:
            logger.warning(f"Message with ID {message_id} not found for deletion")
            raise message_not_found_exception

        await db.delete(db_message)
        await db.commit()
        logger.info(f"Message with ID {message_id} deleted")
        return db_message
    except HTTPException:
        logger.warning(f"Message with ID {message_id} not found for update")
        raise message_not_found_exception
    except Exception as e:
        logger.error(f"Unhandled exception: {e.__class__.__name__}\nreturning 400")
        logger.error(f"Database error occurred while deleting message with ID {message_id}: {str(e)}")
        raise unhandled_exception
