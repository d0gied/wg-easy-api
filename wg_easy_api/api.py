from datetime import datetime
from functools import wraps
import json
from aiohttp import ClientSession
from aiohttp.cookiejar import CookieJar
from . import models

from pydantic import BaseModel, RootModel, TypeAdapter


class NotAuthenticatedError(Exception):
    pass


class WGEasyAPIConnector:
    @staticmethod
    def autocontextmanager(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            if not self.is_connected:
                async with self as client:
                    return await func(client, *args, **kwargs)
            else:
                return await func(self, *args, **kwargs)

        return wrapper

    def __init__(self, base_url: str):
        self.base_url = base_url.strip("/")
        self.api_url = f"{self.base_url}/api"
        self.session: ClientSession
        self.cookies: CookieJar = None
        self.is_connected = False

    async def __aenter__(self):
        self.session = ClientSession(cookie_jar=self.cookies)
        if not self.cookies:
            response = await self.session.get(
                f"{self.base_url}/"
            )  # Just to get cookies
            if not (200 <= response.status < 300):
                await self.session.close()
                response.raise_for_status()
        self.is_connected = True
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.cookies = self.session.cookie_jar
        self.is_connected = False
        await self.session.close()

    @autocontextmanager
    async def raw_request(
        self,
        method: str,
        path: str,
        *,
        data: BaseModel | dict | None = None,
        params: dict = None,
    ) -> str:
        if isinstance(data, BaseModel):
            data = data.model_dump_json()
        elif isinstance(data, dict):
            data = json.dumps(data).encode()

        async with self.session.request(
            method,
            f"{self.api_url}/{path}",
            data=data,
            params=params,
        ) as response:
            if response.status == 401:
                raise NotAuthenticatedError("You need to authenticate first")
            response.raise_for_status()
            return await response.text()
    
    @autocontextmanager
    async def get_image(self, path: str) -> bytes:
        async with self.session.get(f"{self.api_url}/{path}") as response:
            if response.status == 401:
                raise NotAuthenticatedError("You need to authenticate first")
            response.raise_for_status()
            return await response.read()

    async def model_request[
        T
    ](
        self,
        method: str,
        path: str,
        output_type: type[T],
        *,
        data: BaseModel | dict | None = None,
        params: dict = None,
    ) -> T:
        return TypeAdapter(output_type).validate_json(
            await self.raw_request(method, path, data=data, params=params)
        )

    async def authenticate(self, password: str, *, remember: bool = False):
        try:
            await self.model_request(
                "POST",
                "session",
                dict,
                data={"password": password, "remember": remember},
            )
            return True
        except NotAuthenticatedError:
            return False

    async def get_release(self) -> int:
        return await self.model_request("GET", "release", int)

    async def get_language(self) -> str:
        return await self.model_request("GET", "lang", str)

    async def get_remember_me_enabled(self) -> bool:
        return await self.model_request("GET", "remember-me", bool)

    # TODO: GET /ui-traffic-stats
    # TODO: GET /ui-chart-type
    # TODO: GET /wg-enable-one-time-links
    # TODO: GET /wg-enable-expire-time

    async def get_session(self):
        return await self.model_request("GET", "session", models.Session)

    # TODO: DELETE /session

    async def get_clients(self):
        return await self.model_request("GET", "wireguard/client", list[models.Client])

    async def create_client(self, name: str, *, expired_date: str = "") -> bool:
        return await self.model_request(
            "POST",
            "wireguard/client",
            models.Success,
            data={"name": name, "expiredDate": expired_date},
        ) == models.Success(success=True)

    async def delete_client(self, client_id: str):
        return await self.model_request(
            "DELETE", f"wireguard/client/{client_id}", models.Success
        ) == models.Success(success=True)

    # TODO: POST /wireguard/client/${clientId}/generateOneTimeLink

    async def enable_client(self, client_id: str):
        return await self.model_request(
            "POST", f"wireguard/client/{client_id}/enable", models.Success
        ) == models.Success(success=True)

    async def disable_client(self, client_id: str):
        return await self.model_request(
            "POST", f"wireguard/client/{client_id}/disable", models.Success
        ) == models.Success(success=True)

    async def udpate_client_name(self, client_id: str, name: str):
        return await self.model_request(
            "PUT",
            f"wireguard/client/{client_id}/name/",
            models.Success,
            data={"name": name},
        ) == models.Success(success=True)

    async def update_client_address(self, client_id: str, address: str):
        return await self.model_request(
            "PUT",
            f"wireguard/client/{client_id}/address/",
            models.Success,
            data={"address": address},
        ) == models.Success(success=True)

    # TODO: PUT /wireguard/client/{client_id}/expireDate/
    # TODO: PUT /wireguard/restore
    # TODO: GET /ui-sort-clients


    async def get_client_config(self, client_id: str):
        return await self.raw_request(
            "GET", f"wireguard/client/{client_id}/configuration"
        )

    async def get_client_qrcode(self, client_id: str) -> bytes:
        """Get the QR code SVG for the client"""
        return await self.get_image(f"wireguard/client/{client_id}/qrcode.svg")