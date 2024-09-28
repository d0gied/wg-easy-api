from wg_easy_api import WGEasy
import pytest
from tests.config import Config

@pytest.mark.asyncio
async def test_client():
    wg_easy = WGEasy(Config.MOCK_ENDPOINT, Config.MOCK_PASSWORD)
    client = await wg_easy.create_client("Test Client")
    assert client.name == "Test Client"
    assert client.enabled == True
    assert client.id is not None
    assert client.created_at is not None
    assert client.updated_at is not None
    assert client.public_key is not None
    assert client.address is not None

    address = client.address

    found_client = await wg_easy.get_client(client.id)
    assert found_client is not None
    assert found_client.name == "Test Client"
    assert found_client.enabled == True
    assert found_client.id == client.id
    assert found_client.address == address

    await wg_easy.rename_client(client.id, "Test Client 2")
    found_client = await wg_easy.get_client(client.id)
    assert found_client.name == "Test Client 2"
    assert found_client.updated_at > client.created_at

    await wg_easy.change_client_address(client.id, "10.20.30.40")
    found_client = await wg_easy.get_client(client.id)
    assert found_client.address == "10.20.30.40"

    await wg_easy.disable_client(client.id)
    found_client = await wg_easy.get_client(client.id)
    assert found_client.enabled == False

    await wg_easy.enable_client(client.id)
    found_client = await wg_easy.get_client(client.id)
    assert found_client.enabled == True

    await wg_easy.get_client_config(client.id)
    await wg_easy.get_client_qrcode(client.id)

    await wg_easy.delete_client(client.id)
    found_client = await wg_easy.get_client(client.id)
    assert found_client is None



