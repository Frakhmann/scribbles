from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_HOST: str = None
    DATABASE_PORT: str = None
    DATABASE_NAME: str = None
    DATABASE_USER: str = None
    DATABASE_PASSWORD: str = None
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    BASE_URL: str = "http://localhost:8000"

    # ДОБАВЬ:
    SMTP_SERVER: str = "mail.scribbles.uz"
    SMTP_PORT: int = 587
    SMTP_USER: str = "info@scribbles.uz"
    SMTP_PASSWORD: str = "Nasaf1986"

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql+psycopg2://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}" \
               f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"

    class Config:
        env_file = ".env"


settings = Settings()
