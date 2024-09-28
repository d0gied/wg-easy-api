from functools import wraps
from .api import WGEasyAPIConnector
from . import models


class WGEasy:
    @staticmethod
    def autoauth(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            if not await self.is_authenticated():
                await self.connector.authenticate(self.password)
            return await func(self, *args, **kwargs)

        return wrapper

    def __init__(self, base_url: str, password: str):
        self.connector = WGEasyAPIConnector(base_url)
        self.password = password

    async def is_authenticated(self):
        return (await self.connector.get_session()).authenticated

    @autoauth
    async def get_clients(self):
        return await self.connector.get_clients()

    @autoauth
    async def get_client(self, client_id: str) -> models.Client | None:
        return next(
            (client for client in await self.get_clients() if client.id == client_id),
            None,
        )

    @autoauth
    async def create_client(self, name: str) -> models.Client:
        await self.connector.create_client(name)
        return (await self.get_clients())[-1]  # Return the last client

    @autoauth
    async def delete_client(self, client_id: str):
        await self.connector.delete_client(client_id)
        return True

    @autoauth
    async def rename_client(self, client_id: str, new_name: str):
        await self.connector.udpate_client_name(client_id, new_name)
        return True

    @autoauth
    async def enable_client(self, client_id: str):
        await self.connector.enable_client(client_id)
        return True

    @autoauth
    async def disable_client(self, client_id: str):
        await self.connector.disable_client(client_id)
        return True

    @autoauth
    async def change_client_address(self, client_id: str, new_address: str):
        await self.connector.update_client_address(client_id, new_address)
        return True

    @autoauth
    async def get_client_config(self, client_id: str):
        return await self.connector.get_client_config(client_id)
    
    @autoauth
    async def get_client_qrcode(self, client_id: str):
        return await self.connector.get_client_qrcode(client_id)