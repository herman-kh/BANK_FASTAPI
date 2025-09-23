from sqlalchemy.future import select
from data.database import get_async_session
from data.models import User
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

async def find_by_username(username:str, db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()
    

