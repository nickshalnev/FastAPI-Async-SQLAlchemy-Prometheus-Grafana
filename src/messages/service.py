from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.messages.models import Message
from src.messages.schemas import MessageReq, MessageUpdate
from src.config import logger


async def create_message(db: AsyncSession, message: MessageReq):
    db_message = Message(text=message.text)
    db.add(db_message)
    await db.commit()
    await db.refresh(db_message)
    logger.info(f"Message created with ID {db_message.id}")
    return db_message


async def get_messages(db: AsyncSession, skip: int = 0, limit: int = 10):
    result = await db.execute(select(Message).offset(skip).limit(limit))
    messages = result.scalars().all()
    logger.info(f"Retrieved {len(messages)} messages")
    return messages


async def get_message(db: AsyncSession, message_id: int):
    result = await db.execute(select(Message).filter(Message.id == message_id))
    message = result.scalars().first()
    if message is None:
        logger.warning(f"Message with ID {message_id} not found")
    else:
        logger.info(f"Message with ID {message_id} retrieved")
    return message


async def update_message(db: AsyncSession, message_id: int, message: MessageUpdate):
    result = await db.execute(select(Message).filter(Message.id == message_id))
    db_message = result.scalars().first()
    if not db_message:
        logger.warning(f"Message with ID {message_id} not found for update")
        return None

    if message.text:
        db_message.text = message.text

    await db.commit()
    await db.refresh(db_message)
    logger.info(f"Message with ID {message_id} updated")
    return db_message


async def delete_message(db: AsyncSession, message_id: int):
    result = await db.execute(select(Message).filter(Message.id == message_id))
    db_message = result.scalars().first()
    if not db_message:
        logger.warning(f"Message with ID {message_id} not found for deletion")
        return None

    await db.delete(db_message)
    await db.commit()
    logger.info(f"Message with ID {message_id} deleted")
    return db_message
