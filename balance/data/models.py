from sqlalchemy import Column, Integer, String, Numeric
from decimal import Decimal

from data.database import Base    


class Dollars(Base):
    __tablename__ = "usd"
    
    currency_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, unique=True)
    amount = Column(Numeric(precision=18, scale=2), nullable=False, default=0)

    def to_dict(self):
        return {
            "id": self.currency_id,
            "user_id": self.user_id,
            "amount": Decimal(self.amount) if self.amount else 0.0,
            "currency": "USD"
        }

class Euro(Base):
    __tablename__ = "eur"
    
    currency_id = Column(Integer, primary_key=True, index=True,  autoincrement=True)
    user_id = Column(Integer, unique=True)
    amount = Column(Numeric(precision=18, scale=2), nullable=False, default=0)

    def to_dict(self):
        return {
            "id": self.currency_id,
            "user_id": self.user_id,
            "amount": Decimal(self.amount) if self.amount is not None else 0.0,
            "currency": "EUR"
        }

class Bel_rubles(Base):
    __tablename__ = "byn"
    
    currency_id = Column(Integer, primary_key=True, index=True,  autoincrement=True)
    user_id = Column(Integer, unique=True)
    amount = Column(Numeric(precision=18, scale=2), nullable=False, default=0)

    def to_dict(self):
        return {
            "id": self.currency_id,
            "user_id": self.user_id,
            "amount": Decimal(self.amount) if self.amount is not None else 0.0,
            "currency": "BYN"
        }

class Rubles(Base):
    __tablename__ = "rub"
    
    currency_id = Column(Integer, primary_key=True, index=True,  autoincrement=True)
    user_id = Column(Integer, unique=True)
    amount = Column(Numeric(precision=18, scale=2), nullable=False, default=0)

    def to_dict(self):
        return {
            "id": self.currency_id,
            "user_id": self.user_id,
            "amount": Decimal(self.amount) if self.amount is not None else 0.0,
            "currency": "RUB"
        }
    
class UserEmails(Base):
    __tablename__ = "email_and_id"

    id = Column(Integer, primary_key=True, index=True,  autoincrement=True)
    user_id = Column(Integer, unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "email":self.email
        }
