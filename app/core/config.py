from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = None
    DATABASE_HOST: str = None
    DATABASE_PORT: str = None
    DATABASE_NAME: str = None
    DATABASE_USER: str = None
    DATABASE_PASSWORD: str = None
    SECRET_KEY: str 
    ALGORITHM: str = "HS256"

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql+psycopg2://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}" \
               f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"

    class Config:
        env_file = ".env"

settings = Settings()
