from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import String, CheckConstraint
from data.database import Base, str_uniq, int_pk


class User(Base):
    id: Mapped[int_pk]
    username: Mapped[str] = mapped_column(String(length=100), nullable=False, unique=True)
    email: Mapped[str_uniq] = mapped_column(String(length=255))
    hashed_password: Mapped[str] = mapped_column(String(length=255), nullable=False)
    status: Mapped[str] = mapped_column(String(length=10), nullable=False, default='admin')
    age: Mapped[int] = mapped_column(nullable=False)

    __table_args__ = (
        CheckConstraint('age >= 14', name='check_user_age_min'),
        CheckConstraint('age <= 120', name='check_user_age_max'),
    )