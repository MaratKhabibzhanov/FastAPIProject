from dataclasses import dataclass

from environs import Env


@dataclass
class DatabaseConfig:
    database_url: str


@dataclass
class Config:
    db: DatabaseConfig
    SECRET_KEY: str
    debug: bool
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    MINIMUM_APP_VERSION: str = "0.0.2"
    ALGORITHM: str = "HS256"


def load_config(path: str = None) -> Config:
    env = Env()
    env.read_env(path)  # Загружаем переменные окружения из файла .env

    return Config(
        db=DatabaseConfig(database_url=env("DATABASE_URL")),
        SECRET_KEY=env("SECRET_KEY"),
        debug=env.bool("DEBUG", default=False),
        ACCESS_TOKEN_EXPIRE_MINUTES=15,
        REFRESH_TOKEN_EXPIRE_MINUTES=7 * 24 * 60,
    )
