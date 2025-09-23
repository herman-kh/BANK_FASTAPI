import os
import base64
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SECRET_KEY: str
    REFRESH_TOKEN_SECRET_KEY: str

    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    JWT_ALGORITHM: str
    JWT_EXPIRE_MINUTES: str
    JWT_REFRESH_DAYS: str

    SECRET_KEY: str
    REFRESH_TOKEN_SECRET_KEY: str

    KAFKA_BOOTSTRAP_SERVERS : str
    KAFKA_USER_CREATED_TOPIC: str
    KAFKA_USER_CODE_FOR_REGISTRATION: str
    KAFKA_MESSAGE_FOR_ALL_USERS: str

    VERIFICATION_CODES_KEY: str = base64.b64encode(os.urandom(32)).decode()

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")


    )


settings = Settings()


def get_db_url():
    return (f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@"
            f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
