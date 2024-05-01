import datetime as dt
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import Column, Integer, DateTime, Enum, func
from sqlalchemy.orm import declarative_base
from sqlalchemy.future import select


import config
from settings import ALIVE, DEAD, FINISHED, Stage


Base = declarative_base()
DATABASE_URL = f'postgresql+asyncpg://{config.DB_USERNAME}:{config.DB_PASSWORD}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}'
engine = create_async_engine(DATABASE_URL)
Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default = func.timezone('UTC', func.now()))
    status = Column(Enum(ALIVE, DEAD, FINISHED, name='user_status'), default = ALIVE)
    status_updated_at = Column(DateTime, default = func.timezone('UTC', func.now()))
    stage = Column(Integer, default = 1)
    last_message = Column(Integer, default = 0)


async def create_database() -> None:
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as ex:
        print(ex)


async def add_user(user_id: int, stage: int = 1) -> None:
    user: User = User(id = user_id, stage = stage)
    async with Session() as db:
        db.add(user)
        
        try:
            await db.commit()
        except:
            pass
            

async def get_user(user_id: int) -> Optional[User]:
    async with Session() as db:
        user = await db.get(User, user_id)
        return user


async def get_users_to_notify(stage: Stage) -> Optional[List[User]]:
    async with Session() as db:
        time_filter = dt.datetime.utcnow() - dt.timedelta(minutes=stage.await_time)
        users = await db.execute(select(User).where(User.status == ALIVE,
                                                    User.stage == stage.stage_num,
                                                    User.status_updated_at <= time_filter,
                                                    ))
        users = users.scalars().all()

        return users


async def update_status(user_id: int, status: str, message_id: int = 0) -> None:
    async with Session() as db:
        user = await db.get(User, user_id)

        user.status = status
        user.status_updated_at = dt.datetime.utcnow()

        if status == ALIVE or status == FINISHED:
            user.stage += 1

        if message_id:
            user.last_message = message_id

        try:
            await db.commit()
        except:
            pass


async def update_last_message(user_id: int, message_id: int) -> None:
    async with Session() as db:
        user = await db.get(User, user_id)
        user.last_message = message_id

        try:
            await db.commit()
        except:
            pass

