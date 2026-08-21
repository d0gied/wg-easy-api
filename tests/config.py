from typing import Callable, ClassVar, NoReturn

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def require(name: str) -> Callable[[], NoReturn]:
    def r() -> NoReturn:
        raise ValueError(f"Set {name.upper()} in .env")

    return r


class EnvConfig(BaseSettings):
    wg_easy_url: str = Field(default_factory=require("wg_easy_url"))
    wg_easy_username: str = Field(default_factory=require("wg_easy_user"))
    wg_easy_password: str = Field(default_factory=require("wg_easy_password"))

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=".env", case_sensitive=False
    )


env_config = EnvConfig()
