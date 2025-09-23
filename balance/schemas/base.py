from pydantic import BaseModel, Field
from typing import Optional, Union
from decimal import Decimal
from enum import Enum

class BalanceOperationRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50, example="german")
    currency: str = Field(..., pattern="^(USD|EUR|RUB|BYN)$", example="USD")
    amount: Decimal = Field(..., gt=0, example=100.50)


class BalanceResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    user_id: int
    currency: Optional[str] = None
    amount: Optional[Decimal] = None
    email: Optional[str] = None
    new_balance: Optional[Decimal] = None
    error: Optional[str] = None


class AdminUpdateExchangeRateResponce(BaseModel): 
    usd_to_eur :Decimal
    eur_to_usd: Decimal 
    usd_to_rub: Decimal
    rub_to_usd: Decimal 
    usd_to_byn: Decimal
    byn_to_usd: Decimal
    eur_to_rub: Decimal
    rub_to_eur: Decimal
    eur_to_byn: Decimal
    byn_to_eur: Decimal
    rub_to_byn: Decimal
    byn_to_rub: Decimal

class ExchangeRateKeys(str, Enum):
    usd_to_eur = "usd_to_eur"
    eur_to_usd = "eur_to_usd"
    usd_to_rub = "usd_to_rub"
    rub_to_usd = "rub_to_usd"
    usd_to_byn = "usd_to_byn"
    byn_to_usd = "byn_to_usd"
    eur_to_rub = "eur_to_rub"
    rub_to_eur = "rub_to_eur"
    eur_to_byn = "eur_to_byn"
    byn_to_eur = "byn_to_eur"
    rub_to_byn = "rub_to_byn"
    byn_to_rub = "byn_to_rub"

class UpdateCommision(BaseModel):
    message:str
    commision: Decimal

class MoneyAmount(BaseModel):
    amount: Decimal
    currency: str

class ExchangeOperationResponse(BaseModel):
    success: bool
    withdraw: Optional[dict] = None
    deposit: Optional[dict] = None
    exchange_rate: Optional[float] = None
    error: Optional[str] = None
    user_id: int

class WithdrawOperation(BaseModel):
    user_id: int
    amount_with_commision: Decimal

class DepositOperation(BaseModel):
    user_id: int 
    amount: Decimal

class ResponseForTranferOperation(BaseModel):
    success: bool
    currency: Optional[str] = None
    withdraw: Optional[WithdrawOperation] = None
    deposit: Optional[DepositOperation] = None
    error: Optional[str] = None

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    user_id: int

class ErrorResponseWithoutUserId(BaseModel):
    success: bool = False
    error: str

class CurranciesAndAmount(BaseModel):
    USD: Decimal
    EUR: Decimal
    BYN: Decimal
    RUB: Decimal


class NewBalanceResponse(BaseModel):
    success: bool
    user_id: int
    accounts: CurranciesAndAmount