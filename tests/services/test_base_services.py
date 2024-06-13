import pytest
import asyncio
from datetime import datetime
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from master_server.database.user.model import User


@pytest.mark.anyio
async def test_base_model_save(session: AsyncSession):
    model_instance = User(email="test@test.com")

    await model_instance.save(session)

    # Verify it was saved
    statement = select(User).where(User.email == "test@test.com")
    result = await session.exec(statement)
    db_instance = result.one()

    assert db_instance is not None
    assert db_instance.id == model_instance.id
    assert db_instance.email == "test@test.com"


# Test for Base model delete method
@pytest.mark.anyio
async def test_base_model_delete(session: AsyncSession):
    model_instance = User(email="test@test.com")

    await model_instance.save(session)
    await model_instance.delete(session)

    # Verify it was deleted
    statement = select(User).where(User.email == "test@test.com")
    result = await session.exec(statement)
    db_instance = result.first()

    assert db_instance is None


# Test for Base model update method
@pytest.mark.anyio
async def test_base_model_update(session: AsyncSession):
    model_instance = User(email="test@test.com")

    await model_instance.save(session)
    await model_instance.update(session, email="updated@test.com")

    # Verify it was updated
    statement = select(User).where(User.email == "updated@test.com")
    result = await session.exec(statement)
    db_instance = result.one()

    assert db_instance is not None
    assert db_instance.id == model_instance.id
    assert db_instance.email == "updated@test.com"


# Test for TimeStampMixin
@pytest.mark.anyio
async def test_timestamp_mixin(session: AsyncSession):
    before_creation = datetime.now()
    model_instance = User(email="test1@test.com")
    await model_instance.save(session)
    after_creation = datetime.now()

    assert before_creation <= model_instance.created_at <= after_creation
    assert before_creation <= model_instance.updated_at <= after_creation

    await model_instance.update(session, email="updated@test.com")
    updated_time = model_instance.updated_at

    assert updated_time > model_instance.created_at

    # Wait for a second to ensure the updated_at timestamp changes
    await asyncio.sleep(1)

    # Update again
    await model_instance.update(session, email="updated_again@test.com")
    assert model_instance.updated_at > updated_time
