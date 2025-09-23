from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import asc, delete
from data.models import User
from config.security import hash_password

async def get_user_by_email(session: AsyncSession, email: str):
    result = await session.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create_user(session: AsyncSession, username: str, email: str, password: str, age: int):
    hashed_password = await hash_password(password) 
    user = User(username=username, email=email, hashed_password=hashed_password, status='user', age=age)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

class AdminTools:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def get_all_users(self):
        result = await self.db.execute(select(User).order_by(asc(User.id)))
        users = result.scalars().all()
        return users
    
    async def update_user_status(self, user_id_for_new_status:int, new_status:str):
        result = await self.db.execute(select(User).where(User.id == user_id_for_new_status))
        account = result.scalar_one_or_none()
        account.status=new_status
        await self.db.commit()
        await self.db.refresh(account)
        return account
    
    async def delete_user(self, user_id:int):
        await self.db.execute(delete(User).where(User.id == user_id))
        await self.db.commit()
        return {"success": True}


    