from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    access_token_expire_minutes: int = 10080
    r2_account_id: str
    r2_access_key_id: str
    r2_secret_access_key: str
    r2_bucket_name: str
    r2_public_base_url: str
    kling_access_key: str = ""
    kling_secret_key: str = ""
    runway_api_key: str = ""

    class Config:
        env_file = ".env"

settings = Settings()
