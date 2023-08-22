"""
Application Configuration
"""

from pydantic_settings import BaseSettings


class AppConfig(BaseSettings):
    """
    Application configuration class.

    Attributes:
        secret_key (str): Secret key.
        refresh_rate (int): Refresh rate.

    Config:
        env_file (str): Configuration file path.
    """
    secret_key: str
    refresh_rate: int

    class Config:
        env_file = "config.toml"


app_config = AppConfig()
