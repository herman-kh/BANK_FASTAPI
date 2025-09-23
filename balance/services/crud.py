from sqlalchemy.orm import Session
from config.config import settings
from data.models import Dollars, Euro, Bel_rubles, Rubles, UserEmails
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import json
from decimal import Decimal
from sqlalchemy import asc
from typing import Optional

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def create_id_and_email_note(self, user_id:int, email:str) -> dict:
        try:
            result = await self.db.execute(
                select(UserEmails).where(UserEmails.user_id == user_id)
            )
            existing_user = result.scalar_one_or_none()
            if existing_user:
                return {
                    "success": False,
                    "error": f"User {user_id} already exists",
                    "user_id": user_id
                }

    
            new_user = UserEmails(user_id=user_id, email=email)
            logger.info(f"Adding new user email: user_id={user_id}, email={email}")
            self.db.add(new_user)

            await self.db.commit()
            await self.db.refresh(new_user)

            return {
                "success": True,
                "user_id": new_user.user_id,
                "email": new_user.email
            }

        except Exception as e:
            await self.db.rollback()
            return {
                "success": False,
                "error": str(e),
                "user_id": user_id
            }
            
    
    async def create_user(self, user_id: int) -> dict:
        try:
            existing_user = await self.db.execute(
            select(Dollars).where(Dollars.user_id == user_id)
        )
            if existing_user.scalar_one_or_none():
                return {
                "success": False,
                "error": f"User {user_id} already exists",
                "user_id": user_id
            }

            usd_account = Dollars(user_id=user_id, amount=0)
            euro_account = Euro(user_id=user_id, amount=0)
            rub_account = Rubles(user_id=user_id, amount=0)
            byn_account = Bel_rubles(user_id=user_id, amount=0)
            
            self.db.add_all([usd_account, euro_account, byn_account, rub_account])
            await self.db.commit() 


            return {
                "success": True,
                "user_id": user_id,
                "accounts": {
                    "USD": usd_account.to_dict(),
                    "EUR": euro_account.to_dict(),
                    "RUB": rub_account.to_dict(),
                    "BYN": byn_account.to_dict()
                }
            }
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to create user {user_id}: {str(e)}") 
            return {
                "success": False,
                "error": str(e),
                "user_id": user_id
            }
            
    async def get_email_by_user_id(self, user_id: int) -> Optional[str]:
        result = await self.db.execute(select(UserEmails.email).where(UserEmails.user_id == user_id))
        email = result.scalar_one_or_none()
        return email

    async def update_currency_balance(self, user_id: int, currency: str, amount: Decimal) -> dict:
        try:
            currency_models = {
            "USD": Dollars,
            "EUR": Euro,
            "RUB": Rubles, 
            "BYN": Bel_rubles
        }
            
            model_class = currency_models.get(currency.upper())
            if not model_class:
                return {
                    "success": False,
                    "error": f"Invalid currency: {currency}",
                    "user_id": user_id
                }
            
            result = await self.db.execute(select(model_class).where(model_class.user_id == user_id))
            email = await self.db.execute(select(UserEmails).where(UserEmails.user_id == user_id))
            email_result = email.scalar_one_or_none()
            account = result.scalar_one_or_none()

            if not email_result:
                return {
                "success": False,
                "error": f"Email not found in database",
                "user_id": user_id
            }

            if not account:
                return {
                "success": False,
                "error": f"User {user_id} not found in {currency} database",
                "user_id": user_id
            }
            if amount <= 0:
                return {
                "success": False,
                "error": "Deposit amount must be positive",
                "user_id": user_id
                }
            account.amount = Decimal(account.amount)
            account.amount += amount

            await self.db.commit()

            message = f"Deposited {amount} {currency}"


            return  {
            "success": True,
            "message": message,
            "user_id": user_id,
            "currency": currency,
            "amount": str(amount),
            "email":email_result.email,
            "new_balance": str(account.amount),
        }

        except Exception as e:
            await self.db.rollback() 
            logger.error(f"Failed to create user {user_id}: {str(e)}")
            return {
             "success": False,
            "error": str(e),
             "user_id": user_id
             }
    
    async def send_user_balance(self, user_id: int) -> dict:
        try:
            currency_models = {
            "USD": Dollars,
            "EUR": Euro,
            "RUB": Rubles, 
            "BYN": Bel_rubles
        }
            
            accounts = []

            model_class = currency_models.get('USD')
            result = await self.db.execute(select(model_class).where(model_class.user_id == user_id))
            account = result.scalar_one_or_none()
            accounts.append(account)


            usd = Decimal(account.amount)
            
            model_class = currency_models.get('EUR')
            result = await self.db.execute(select(model_class).where(model_class.user_id == user_id))
            account = result.scalar_one_or_none()
            accounts.append(account)

            eur = Decimal(account.amount)

            model_class = currency_models.get('BYN')
            result = await self.db.execute(select(model_class).where(model_class.user_id == user_id))
            account = result.scalar_one_or_none()
            accounts.append(account)
            byn = Decimal(account.amount)

            model_class = currency_models.get('RUB')
            result = await self.db.execute(select(model_class).where(model_class.user_id == user_id))
            account = result.scalar_one_or_none()
            accounts.append(account)

            rub = Decimal(account.amount)
            
            for account in accounts:
                if not account:
                    return {
                        "success": False,
                        "error": f"User {user_id} not found in databases",
                        "user_id": user_id
                    }
                    
            
            return{
                'USD': usd,
                'EUR': eur,
                'BYN': byn,
                'RUB': rub,
            }
        except Exception as e:
            await self.db.rollback() 
            logger.error(f"Failed to create user {user_id}: {str(e)}")
            return {
             "success": False,
            "error": str(e),
             "user_id": user_id
             }
        
    async def change_money(self, user_id: int, currency_to_sell: str, amount: Decimal, currency_to_buy: str):
        try: 
            if currency_to_sell == currency_to_buy:
                return{
                    "success": False,
                    "error": "Currency_to_sell and currency_to_buy can't be identic",
                    "user_id": user_id
                }
            operation = f'{currency_to_sell.lower()}_to_{currency_to_buy.lower()}'
            currency_models = {
            "USD": Dollars,
            "EUR": Euro,
            "RUB": Rubles, 
            "BYN": Bel_rubles
        }
            
            model_class = currency_models.get(currency_to_sell.upper())
            if not model_class:
                return {
                    "success": False,
                    "error": f"Invalid currency: {currency_to_sell}",
                    "user_id": user_id
                }
            result = await self.db.execute(select(model_class).where(model_class.user_id == user_id))
            account = result.scalar_one_or_none()

            if not account:
                return {
                "success": False,
                "error": f"User {user_id} not found in database",
                "user_id": user_id == user_id
            }

            if amount > Decimal(account.amount):
                return {
                "success": False,
                "error": "You don't have enough money",
                "user_id": user_id
                }
            
            if amount <= 0:
                return {
                "success": False,
                "error": "Deposit amount must be positive",
                "user_id": user_id
                }
            
            account.amount = Decimal(account.amount)
            account.amount -= Decimal(amount)

            await self.db.commit()
            await self.db.refresh(account)

            with open(settings.JSON_FILE, 'r', encoding='utf-8') as f:
                dict_from_json = json.load(f)
            rate = dict_from_json[operation]
            amount_in_new_currency = amount * Decimal(rate)

            model_class = currency_models.get(currency_to_buy.upper())
            if not model_class:
                return {
                    "success": False,
                    "error": f"Invalid currency: {currency_to_sell}",
                    "user_id": user_id
                }

            result = await self.db.execute(select(model_class).where(model_class.user_id == user_id))
            account = result.scalar_one_or_none()

            if not account:
                return {
                "success": False,
                "error": f"User {user_id} not found in database",
                "user_id": user_id 
            }
            
            account.amount = Decimal(account.amount)
            account.amount += amount_in_new_currency

            await self.db.commit()
            await self.db.refresh(account)

            return{
                "success": True,
                "withdraw":{
                    "amount": str(amount),
                    "currency": currency_to_sell
                },
                "deposit":{
                    "amount":str(round(amount_in_new_currency, 2)),
                    "currency": currency_to_buy
                },
                "exchange_rate": rate,
                "user_id": user_id
                
            } 
            
        except Exception as e:
            await self.db.rollback() 
            logger.error(f"{user_id}: {str(e)}")
            return {
             "success": False,
            "error": str(e),
             "user_id": user_id
             }
        
    async def transfer_money(self, user_id: int, user_id_for_transfer: int, currency: str, amount: Decimal):
        try:
            currency_models = {
            "USD": Dollars,
            "EUR": Euro,
            "RUB": Rubles, 
            "BYN": Bel_rubles
        }
            with open(settings.JSON_FILE2, 'r', encoding='utf-8') as f:
                dict_from_json = json.load(f)
            
            rate = dict_from_json["commision_for_transfers"]
            amount_with_commision = amount*Decimal(rate)
            data_name = currency_models[currency]
            result = await self.db.execute(select(data_name).where(data_name.user_id == user_id))
            account = result.scalar_one_or_none()
            if not account:
                return {"success": False,
                        "error": f"User {user_id} not found in database",
                        "user_id": user_id == user_id}
            if amount <= 0:
                return {"success": False,
                        "error": "Amount must be positive",
                        "user_id": user_id == user_id}
            if amount_with_commision > account.amount :
                return {"success": False,
                        "error": "You don't have enough money",
                        "user_id": user_id == user_id}
            
            account.amount = Decimal(account.amount)
            account.amount -= amount_with_commision

            await self.db.commit()
            await self.db.refresh(account)

            result = await self.db.execute(select(data_name).where(data_name.user_id == user_id_for_transfer))
            account_another_user = result.scalar_one_or_none()
            if not account:
                return {"success": False,
                        "error": "User {user_id} not found in database",
                        "user_id": user_id == user_id_for_transfer}
            
            account_another_user.amount = Decimal(account_another_user.amount)
            account_another_user.amount += amount

            await self.db.commit()
            await self.db.refresh(account_another_user)

            return {
                'success': True,
                'currency': currency,
                'withdraw':{
                    'user_id':user_id,
                    'amount_with_commision': str(amount_with_commision)
                },
                'deposit':{
                    'user_id': user_id_for_transfer,
                    'amount' : str(amount)
                }
            }


        except Exception as e:
            await self.db.rollback()
            logger.error(f"{user_id}: {str(e)}")
            return{
                "success": False,
                "error":str(e),
                "user_id": user_id
            } 
        
class AdminService:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def get_all_users(self):
        result = await self.db.execute(select(UserEmails).order_by(asc(UserEmails.id)))
        users = result.scalars().all()
        return users
    
    async def update_exchange_rate(self, exchange_rate_you_want_to_change: str, new_index: Decimal):
        try:
            if new_index <= 0:
                return {"success": False,
                        "error": "Amount must be positive"}
            with open(settings.JSON_FILE, 'r', encoding='utf-8') as f:
                dict_from_json = json.load(f)
            dict_from_json[exchange_rate_you_want_to_change]=new_index

            with open(settings.JSON_FILE, 'w', encoding='utf-8') as f:
                json.dump(str(dict_from_json), f, ensure_ascii=False, indent=4)
                
            return dict_from_json
        except Exception as e:
             logger.error(f"Failed to update exchange rate")
             return {
             "success": False,
            "error": str(e),
             }
        
    async def update_commission_for_transfers(self, new_index):
        try:
            with open(settings.JSON_FILE2, 'r', encoding='utf-8') as f:
                dict_from_json = json.load(f)
            dict_from_json["commision_for_transfers"]=new_index

            with open(settings.JSON_FILE2, 'w', encoding='utf-8') as f:
                json.dump(dict_from_json, f, ensure_ascii=False, indent=4)

            return dict_from_json

        except Exception as e:
             logger.error(f"Failed to update exchange rate")
             return {
             "success": False,
            "error": str(e),
             }
