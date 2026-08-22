from typing import TypeVar, overload

from aiohttp import ClientResponse, ClientSession, encode_basic_auth
from pydantic import BaseModel, TypeAdapter

import wg_easy_api.models as models

T = TypeVar("T")
M = TypeVar("M", bound=BaseModel)


@overload
async def validate_response(resp: ClientResponse, model: TypeAdapter[T]) -> T: ...


@overload
async def validate_response(resp: ClientResponse, model: type[M]) -> M: ...


async def validate_response(
    resp: ClientResponse, model: type[M] | TypeAdapter[T]
) -> M | T:
    json = await resp.json()  # pyright: ignore[reportAny]
    # print(json)
    if isinstance(model, TypeAdapter):
        return model.validate_python(json)
    else:
        return model.model_validate(json)


class WGEasy:
    base_url: str
    api_url: str
    auth: str

    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip("/")
        self.api_url = f"{self.base_url}/api"
        self.auth = encode_basic_auth(username, password)

    def _get_session(self):
        return ClientSession(headers={"Authorization": self.auth})

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, str] | None = None,
    ) -> ClientResponse:
        url = f"{self.api_url}/{path.lstrip('/')}"
        async with self._get_session() as session:
            resp = await session.request(method, url, json=json)
            if not resp.ok:
                json = await resp.json()  # pyright: ignore[reportAny]
                print(json)
                error_detail = models.ApiErrorModel.model_validate(json)
                raise models.ApiError(error_detail)
            return resp

    async def get_clients(self) -> list[models.Client]:
        resp = await self._request(
            "GET",
            "client",
        )
        return await validate_response(resp, TypeAdapter(list[models.Client]))

    async def get_client(self, client_id: models.ClientID) -> models.Client:
        resp = await self._request(
            "GET",
            f"client/{client_id}",
        )
        return await validate_response(resp, models.Client)

    async def create_client(
        self, client_data: models.ClientPost
    ) -> models.ClientPostReturn:
        resp = await self._request(
            "POST",
            "client",
            json=client_data.model_dump(),
        )
        return await validate_response(resp, models.ClientPostReturn)

    async def update_client(self, client: models.Client) -> models.Success:
        resp = await self._request(
            "POST",
            f"client/{client.id}",
            json=client.model_dump(),
        )
        return await validate_response(resp, models.Success)

    async def delete_client(self, client_id: models.ClientID) -> models.Success:
        resp = await self._request(
            "DELETE",
            f"client/{client_id}",
        )
        return await validate_response(resp, models.Success)

    async def enable_client(self, client_id: models.ClientID) -> models.Success:
        resp = await self._request(
            "POST",
            f"client/{client_id}/enable",
        )
        return await validate_response(resp, models.Success)

    async def disable_client(self, client_id: models.ClientID) -> models.Success:
        resp = await self._request(
            "POST",
            f"client/{client_id}/disable",
        )
        return await validate_response(resp, models.Success)

    async def get_client_config(self, client_id: models.ClientID) -> str:
        resp = await self._request(
            "GET",
            f"client/{client_id}/configuration",
        )
        return await resp.text()
