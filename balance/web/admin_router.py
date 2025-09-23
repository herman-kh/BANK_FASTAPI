from fastapi import APIRouter, Depends, HTTPException, Query
from services.crud import AdminService
from sqlalchemy.ext.asyncio import AsyncSession
from data.database import get_db
from schemas.base import AdminUpdateExchangeRateResponce, ExchangeRateKeys, UpdateCommision, ErrorResponseWithoutUserId
from services.utils import decode_access_token
from config.config import settings
from decimal import Decimal
from typing import Union

router = APIRouter(prefix='/admin', tags=['admin'])

@router.post('/update_exchange_rate', response_model=Union[AdminUpdateExchangeRateResponce, ErrorResponseWithoutUserId])
async def update_exhange_rate(token: str = Query(...), 
                              exchange_rate_you_want_to_change: ExchangeRateKeys = Query(...), 
                              new_index: Decimal = Query(...,),
                              db: AsyncSession = Depends(get_db)):
    token_data=decode_access_token(token)
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid token")
    if token_data.get("status") != 'admin':
        raise HTTPException(
            status_code=403,
            detail="You aren't admin"
        )
    admin_service = AdminService(db)
    result = await admin_service.update_exchange_rate(
        exchange_rate_you_want_to_change=exchange_rate_you_want_to_change,
        new_index=new_index)
    return result

@router.post('/update_commission_for_transfers', response_model = Union[UpdateCommision, ErrorResponseWithoutUserId])
async def update_commission_for_transfers(token: str = Query(...), new_index: float = Query(..., ge=1), db: AsyncSession = Depends(get_db)):
    token_data=decode_access_token(token)
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid token")
    if token_data.get("status") != 'admin':
        raise HTTPException(
            status_code=403,
            detail="You aren't admin"
        )
    admin_tools = AdminService(db)
    result = await admin_tools.update_commission_for_transfers(new_index=new_index)
    return {
        "message":"Commission was successfully updted",
        "commision":result["commision_for_transfers"]}


@router.get("/get_all_users")
async def get_all_users(token: str = Query(...),  db: AsyncSession = Depends(get_db)):
    try:
        token_data = decode_access_token(token=token)
        if not token_data:
            raise HTTPException(status_code=401, detail="Invalid token")
        if token_data.get("status") != 'admin':
            raise HTTPException(
                status_code=403,
                detail="You aren't admin"
            )
        
        admin_tools = AdminService(db)
        result = await admin_tools.get_all_users()
        return result

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )