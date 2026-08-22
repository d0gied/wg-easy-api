import pytest
import pytest_asyncio

import wg_easy_api
from tests.config import env_config
from wg_easy_api import WGEasy


@pytest_asyncio.fixture
async def wg():
    yield WGEasy(
        base_url=env_config.wg_easy_url,
        username=env_config.wg_easy_username,
        password=env_config.wg_easy_password,
    )


@pytest.mark.asyncio
async def test_get_all_clients(wg: WGEasy):
    _ = await wg.get_clients()


@pytest.mark.asyncio
async def test_bad_id(wg: WGEasy):
    with pytest.raises(wg_easy_api.ApiError) as e:
        _ = await wg.get_client(0)
    assert e.value.details.statusCode == 404


@pytest.mark.asyncio
async def test_client_lifecycle(wg: WGEasy):
    client_name = "test_client"
    created_client = await wg.create_client(
        wg_easy_api.ClientPost(name=client_name),
    )

    client_id = created_client.clientId

    found_client = await wg.get_client(client_id)
    assert found_client.enabled == True
    assert found_client.name == client_name

    found_client.name = new_name = "new name"
    found_client.ipv4Address = new_ip = "10.8.0.99"

    _ = await wg.update_client(found_client)
    updated_client = await wg.get_client(client_id)
    assert updated_client.name == new_name
    assert updated_client.ipv4Address == new_ip

    _ = await wg.disable_client(found_client.id)
    found_client = await wg.get_client(found_client.id)
    assert found_client.enabled == False

    _ = await wg.enable_client(found_client.id)
    found_client = await wg.get_client(found_client.id)
    assert found_client.enabled == True

    _ = await wg.get_client_config(found_client.id)

    _ = await wg.delete_client(found_client.id)

    with pytest.raises(wg_easy_api.ApiError):
        found_client = await wg.get_client(found_client.id)
