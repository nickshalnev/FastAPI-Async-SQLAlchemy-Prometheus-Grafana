import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from src.messages.models import Message
from src.messages.schemas import MessageReq, MessageUpdate
from src.messages.service import create_message, get_messages, get_message, update_message, delete_message


@pytest.mark.asyncio
async def test_create_message():
    db_mock = AsyncMock(AsyncSession)
    message_data = MessageReq(text="Hello, World!")

    db_mock.add = MagicMock()
    db_mock.commit = AsyncMock()
    db_mock.refresh = AsyncMock()

    db_message = await create_message(db_mock, message_data)

    assert db_message.text == "Hello, World!"
    assert db_mock.add.called
    assert db_mock.commit.called
    assert db_mock.refresh.called


@pytest.mark.asyncio
async def test_get_messages():
    db_mock = AsyncMock(AsyncSession)
    messages_list = [Message(id=1, text="Message 1"), Message(id=2, text="Message 2")]

    result_mock = MagicMock()
    result_mock.scalars.return_value.all.return_value = messages_list
    db_mock.execute.return_value = result_mock

    messages = await get_messages(db_mock, skip=0, limit=10)

    assert len(messages) == 2
    assert messages[0].text == "Message 1"
    assert messages[1].text == "Message 2"


@pytest.mark.asyncio
async def test_get_message_found():
    db_mock = AsyncMock(AsyncSession)
    test_message = Message(id=1, text="Test message")

    result_mock = MagicMock()
    result_mock.scalars.return_value.first.return_value = test_message
    db_mock.execute.return_value = result_mock

    message = await get_message(db_mock, 1)

    assert message is not None
    assert message.text == "Test message"


@pytest.mark.asyncio
async def test_get_message_not_found():
    db_mock = AsyncMock(AsyncSession)

    result_mock = MagicMock()
    result_mock.scalars.return_value.first.return_value = None
    db_mock.execute.return_value = result_mock

    message = await get_message(db_mock, 999)

    assert message is None


@pytest.mark.asyncio
async def test_update_message_success():
    db_mock = AsyncMock(AsyncSession)
    test_message = Message(id=1, text="Old message")

    result_mock = MagicMock()
    result_mock.scalars.return_value.first.return_value = test_message
    db_mock.execute.return_value = result_mock
    db_mock.commit = AsyncMock()
    db_mock.refresh = AsyncMock()

    update_data = MessageUpdate(text="Updated message")

    updated_message = await update_message(db_mock, 1, update_data)

    assert updated_message.text == "Updated message"
    assert db_mock.commit.called
    assert db_mock.refresh.called


@pytest.mark.asyncio
async def test_update_message_not_found():
    db_mock = AsyncMock(AsyncSession)

    result_mock = MagicMock()
    result_mock.scalars.return_value.first.return_value = None
    db_mock.execute.return_value = result_mock

    update_data = MessageUpdate(text="Updated message")

    updated_message = await update_message(db_mock, 999, update_data)

    assert updated_message is None


@pytest.mark.asyncio
async def test_delete_message_success():
    db_mock = AsyncMock(AsyncSession)
    test_message = Message(id=1, text="Message to delete")

    result_mock = MagicMock()
    result_mock.scalars.return_value.first.return_value = test_message
    db_mock.execute.return_value = result_mock
    db_mock.commit = AsyncMock()

    deleted_message = await delete_message(db_mock, 1)

    assert deleted_message is not None
    assert db_mock.commit.called


@pytest.mark.asyncio
async def test_delete_message_not_found():
    db_mock = AsyncMock(AsyncSession)

    result_mock = MagicMock()
    result_mock.scalars.return_value.first.return_value = None
    db_mock.execute.return_value = result_mock

    deleted_message = await delete_message(db_mock, 999)

    assert deleted_message is None
    assert not db_mock.commit.called
