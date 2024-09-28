# wg-easy-api
API wrapper for wg-easy

# Installation

```bash
pip install wg-easy-api
```

# Usage

```python
from wg_easy_api import WgEasy

wg = WgEasy("http://wg-easy.sample.com:8080", "password")

async def main():
    clients = await wg.get_clients() # Get all clients
    client = await wg.get_client(clients[0].id) # Get client by id

    await wg.create_client("demo_client") # Create client 
    await wg.rename_client(client.id, "new_demo_client") # Rename client
    await wg.change_client_address(client.id, "10.20.30.40") # Change client address

    await wg.disable_client(client.id) # Disable client
    await wg.enable_client(client.id) # Enable client

    with open("client.conf", "w") as f:
        await f.write(await wg.get_client_config(client.id)) # Get client configuration

    with open("qrcode.svg", "wb") as f:
        await f.write(await wg.get_client_qrcode(client.id)) # Get client QR code
    
    await wg.delete_client(client.id) # Delete client


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```
