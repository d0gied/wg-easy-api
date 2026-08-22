# wg-easy-api

API wrapper for [wg-easy](https://github.com/wg-easy/wg-easy) v15.4.0.

Table of Contents
=================

- [wg-easy-api](#wg-easy-api)
- [Installation](#installation)
- [Usage](#usage)
- [Project structure](#project-structure)
- [Docker tests](#docker-tests)
- [Python tests setup](#python-tests-setup)
- [Curl tests](#curl-tests)
- [Pytest](#pytest)
- [Contributors](#contributors)

# Installation

```bash
pip install git+https://github.com/d0gied/wg-easy-api.git@wg-easy-v15.4.0
```

# Usage

```python
from wg_easy_api import (
    ApiError,
    ApiErrorModel,
    Client,
    ClientID,
    ClientPost,
    ClientPostReturn,
    Success,
    WGEasy,
)

wg = WGEasy(
    base_url="http://0.0.0.0:51821",
    username="admin",
    password="secure_password",
)

async def main():
    clients: list[Client] = await wg.get_clients()
    _: Client = await wg.get_client(clients[0].id)

    try:
        _: Client = await wg.get_client(0)
    except ApiError as e:
        details: ApiErrorModel = e.details

    client_info: ClientPostReturn = await wg.create_client(
        ClientPost(name="Bob", expiresAt=None)
    )

    client_id: ClientID = client_info.clientId  # ClientID = int

    _: Success = await wg.disable_client(client_id)
    _: Success = await wg.enable_client(client_id)

    _: str = await wg.get_client_config(client_id)

    _: Success = await wg.delete_client(client_id)
```

# Project structure

```
├── LICENSE
├── poetry.lock
├── pyproject.toml
├── README.md
├── tests
│   ├── config.py
│   ├── curl.sh
│   ├── docker-compose.yml
│   ├── Dockerfile
│   ├── __init__.py
│   └── test_wg_easy.py
└── wg_easy_api
    ├── __init__.py
    ├── models.py
    └── wg_easy.py
```

# Docker tests

To run all tests you can just

```bash
cd tests
docker-compose up -d --build
docker-compose ps -a --format json | jq '{Service, Status}'
```

Services:

- wg-easy
- curl-tests
- pytest

> In [docker-compose.yml](tests/docker-compose.yml) you can find a working wg-easy service, could be helpful.
> If you have problems with setting everything up locally, you can always look at [Dockerfile](tests/Dockerfile) and [docker-compose.yml](tests/docker-compose.yml).

# Python tests setup

`poetry install --with test`

# Curl tests

Simple [bash script](tests/curl.sh) that checks if wg-easy REST API endpoints are correct.

To run:

1. Ensure wg-easy is running (you can simply `docker-compose up -d wg-easy`).
2. [Set up python](#python-tests-setup)
3. Install `bash`, `curl`, `jq`.
4. Add env vars:
   -. `WG_EASY_USERNAME`
   -. `WG_EASY_PASSWORD`
   -. `WG_EASY_URL`
5. Run `bash tests/curl.sh`.

Tested endpoints:

| Method | URL                      | Description                                                 |
| ------ | ------------------------ | ----------------------------------------------------------- |
| GET    | /api/client              | List all WireGuard clients                                  |
| POST   | /api/client              | Create a new client                                         |
| GET    | /api/client/{id}         | Retrieve details of a specific client                       |
| POST   | /api/client/{id}         | Update a client's details (e.g., name, expiry, ipv4Address) |
| POST   | /api/client/{id}/enable  | Enable client                                               |
| POST   | /api/client/{id}/disable | Disable client                                              |
| GET    | /api/client/{id}/config  | Get client’s WireGuard configuration                        |
| DELETE | /api/client/{id}         | Permanently delete a client                                 |

> See [docker tests](#docker-tests) and [script](tests/curl.sh) for more info.

# Pytest

Tests for python module wg_easy_api.
If [curl tests](#curl-tests) fail pytest should fail too.

1. Ensure wg-easy is running (you can simply `docker-compose up -d wg-easy`).
2. [Set up python](#python-tests-setup)
3. Add env vars (can just create .env):
   -. `WG_EASY_USERNAME`
   -. `WG_EASY_PASSWORD`
   -. `WG_EASY_URL`
4. Run `pytest`.

Tests:

- test_get_all_clients
- test_bad_id
- test_client_lifecycle

> See [docker tests](#docker-tests) for more info.

# Contributors

- **d0gied** - Original author
- **AndrewCh** - wg-easy v15.4.0 compatibility updates
