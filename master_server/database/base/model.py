from datetime import datetime
from typing import Any, Optional
from sqlmodel import SQLModel, Field
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import event
from sqlalchemy.exc import SQLAlchemyError, IntegrityError


class Base(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    __name__: str

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        cls.__tablename__ = cls.__name__.lower()

    async def save(self, db_session: AsyncSession):
        try:
            self.model_validate(self.model_dump())  # Validate the current instance

            db_session.add(self)
            await db_session.commit()
        except (SQLAlchemyError, IntegrityError) as ex:
            await db_session.rollback()
            raise ex

    async def delete(self, db_session: AsyncSession):
        try:
            await db_session.delete(self)
            await db_session.commit()
        except SQLAlchemyError as ex:
            await db_session.rollback()
            raise ex

    async def update(self, db: AsyncSession, **kwargs):
        try:
            if not kwargs:
                return True

            updated_instance = self.model_copy(update=kwargs)
            updated_instance.model_validate(
                updated_instance.model_dump()
            )  # This triggers Pydantic validation

            for k, v in kwargs.items():
                setattr(self, k, v)

            await db.commit()
        except SQLAlchemyError as ex:
            await db.rollback()
            raise ex


class TimeStampMixin(SQLModel):
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now)


# Register the event listener
@event.listens_for(TimeStampMixin, "before_update", propagate=True)
def timestamp_before_update(mapper, connection, target):
    target.updated_at = datetime.now()
