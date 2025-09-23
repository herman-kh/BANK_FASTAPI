from fastapi import APIRouter, Depends, HTTPException, Query
from data.database import get_db
from sqlalchemy.orm import Session
from services.crud import UserService
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.base import BalanceResponse, ExchangeOperationResponse, ResponseForTranferOperation, ErrorResponse, NewBalanceResponse, CurranciesAndAmount
from services.utils import decode_access_token
from decimal import Decimal
from typing import Literal, Union
from fastapi.responses import JSONResponse
from services.kafka_producer import producer

router = APIRouter(prefix="/balance", tags=["balance"])

    
@router.post("/deposit", response_model=BalanceResponse)
async def deposit(token: str = Query(...), currency: str = Query(..., regex="^(USD|EUR|RUB|BYN)$"), amount: Decimal =  Query(...), db: Session = Depends(get_db)):
    try:
        token_data = decode_access_token(token=token)
        user_id = token_data.get("id")
        user_service = UserService(db)
        result = await user_service.update_currency_balance(
            user_id=user_id,
            currency=currency,
            amount=amount,
            )
        message_result = (
        f"Hello!\n\n"
        f"Your account has been updated.\n"
        f"User ID: {user_id}\n"
        f"Currency: {currency}\n"
        f"Amount changed: {amount}\n"
        f"New balance: {result["new_balance"]}\n\n"
        f"Thank you for using our service!"
    )
        email = await user_service.get_email_by_user_id(user_id=user_id)
        await producer.send_bill_to_user_email(email=email, message=message_result)
        return result

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
     
@router.get("/watch_balance", response_model=CurranciesAndAmount)
async def send_balance(token: str= Query(...), db: Session=Depends(get_db)):
    try:
        token_data = decode_access_token(token)
        user_id = token_data.get("id")
        user_service = UserService(db)

        
        result = await user_service.send_user_balance(
            user_id=user_id
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
        
 
@router.post("/transfer_money", response_model=ResponseForTranferOperation)
async def transfer_money_for_anothr_user(token: str = Query(...),
                                         user_id_for_transfer: int = Query(...), 
                                         currency: Literal['USD', 'EUR', 'BYN', 'RUB'] = Query(...), 
                                         amount: Decimal = Query(...), 
                                         db: Session=Depends(get_db)):
    try:
        token_data = decode_access_token(token)
        user_id = token_data.get("id")
        user_service = UserService(db)
        result = await user_service.transfer_money(user_id=user_id,
                                                   user_id_for_transfer=user_id_for_transfer,
                                                   currency=currency,
                                                   amount=amount)
        message_result = (
    f"Hello!\n\n"
    f"Transfer completed successfully.\n\n"
    f"Currency: {result['currency']}\n\n"
    f"Withdrawal:\n"
    f" - User ID: {result['withdraw']['user_id']}\n"
    f" - Amount with commission: {result['withdraw']['amount_with_commision']}\n\n"
    f"Deposit:\n"
    f" - User ID: {result['deposit']['user_id']}\n"
    f" - Amount credited: {result['deposit']['amount']}\n\n"
    f"Thank you for using our service!"
)


        email = await user_service.get_email_by_user_id(user_id=user_id)
        await producer.send_bill_to_user_email(email=email, message=message_result)
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@router.post("/change_money", response_model=ExchangeOperationResponse)
async def exchange_money(token: str = Query(...), 
                         currency_to_sell : Literal['USD', 'EUR', 'BYN', 'RUB'] = Query(...), 
                         amount: Decimal = Query(...), 
                         currency_to_buy: Literal['USD', 'EUR', 'BYN', 'RUB'] = Query(...),
                         db: Session=Depends(get_db)):
    try:
        token_data = decode_access_token(token)
        user_id = token_data.get("id")
        user_service = UserService(db)
        result = await user_service.change_money(user_id=user_id,
                                           currency_to_sell=currency_to_sell,
                                           currency_to_buy=currency_to_buy, 
                                           amount=amount)
        message_result = (
    f"Hello!\n\n"
    f"Currency exchange completed successfully.\n\n"
    f"User ID: {result['user_id']}\n"
    f"Exchange rate: {result['exchange_rate']}\n\n"
    f"Withdraw:\n"
    f" - Amount: {result['withdraw']['amount']}\n"
    f" - Currency: {result['withdraw']['currency']}\n\n"
    f"Deposit:\n"
    f" - Amount: {result['deposit']['amount']}\n"
    f" - Currency: {result['deposit']['currency']}\n\n"
    f"Thank you for using our service!"
)
        email = await user_service.get_email_by_user_id(user_id=user_id)
        await producer.send_bill_to_user_email(email=email, message=message_result)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )