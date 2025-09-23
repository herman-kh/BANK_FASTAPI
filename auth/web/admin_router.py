from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from data.database import get_async_session
from services.utils import decode_access_token
from services.crud import AdminTools
from schemas.base import SuccsessfulRegistraionVerify
from data.models import User
from sqlalchemy.future import select
from typing import Literal, List
from services.kafka_producer import producer

router = APIRouter(prefix='/admin', tags=['admin'])

@router.get("/get_all_users", response_model=List[SuccsessfulRegistraionVerify])
async def get_all_users(token: str = Query(...),  db: AsyncSession = Depends(get_async_session)):
    try:
        token_data = decode_access_token(token=token)
        if not token_data:
            raise HTTPException(status_code=401, detail="Invalid token")
        if token_data.get("status") != 'admin':
            raise HTTPException(
                status_code=403,
                detail="You aren't admin"
            )
        
        admin_tools = AdminTools(db)
        result = await admin_tools.get_all_users()
        return result

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    
@router.post("/update_user_status", response_model=SuccsessfulRegistraionVerify)
async def update_status(token: str = Query(...), 
                        user_id_for_new_status: int = Query(...), 
                        new_status: Literal['user', 'admin'] = Query(..., description='Choose admin or user'),
                         db: AsyncSession = Depends(get_async_session)):
    try:
        token_data = decode_access_token(token=token)
        if not token_data:
            raise HTTPException(status_code=401, detail="Invalid token")
        if token_data.get("status") != 'admin':
            raise HTTPException(
                status_code=403,
                detail="You aren't admin"
            )
        admin_tools = AdminTools(db)
        result = await admin_tools.update_user_status(
            user_id_for_new_status=user_id_for_new_status,
            new_status=new_status
        )
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=403,
            detail=str(e)
        )

@router.post("/send_all_users_message")
async def send_all_users_message(token: str, message: str, db: AsyncSession = Depends(get_async_session)):
     try:
        token_data = decode_access_token(token=token)
        if not token_data:
            raise HTTPException(status_code=401, detail="Invalid token")
        if token_data.get("status") != 'admin':
            raise HTTPException(
                status_code=403,
                detail="You aren't admin"
            )
        admin_tools = AdminTools(db)
        users = await admin_tools.get_all_users()
        emails = [i.email for i in users]
        await producer.send_message_to_all_users(message=message, emails=emails)
     except Exception as e:
        raise HTTPException(
            status_code=403,
            detail=str(e)
        )


@router.post("/delete_user")
async def delete_user(token: str = Query(...), 
                        user_id: int = Query(...), 
                         db: AsyncSession = Depends(get_async_session)):
    try:
        token_data = decode_access_token(token=token)
        if not token_data:
            raise HTTPException(status_code=401, detail="Invalid token")
        if token_data.get("status") != 'admin':
            raise HTTPException(
                status_code=403,
                detail="You aren't admin"
            )
        admin_tools = AdminTools(db)
        result = await admin_tools.delete_user(
            user_id=user_id,
        )
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=403,
            detail=str(e)
        )