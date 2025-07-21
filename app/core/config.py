
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_HOST: str
    DATABASE_PORT: str
    DATABASE_NAME: str
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    SECRET_KEY: str 
    ALGORITHM: str = "HS256"

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return f"postgresql+psycopg2://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}" \
               f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"

    class Config:
        env_file = ".env"

settings = Settings()
