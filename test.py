import asyncio
import random
import time
import aiohttp
from uuid import uuid4
import requests


headers = {
    "Authorization": f"Bearer {bearer}"
}

AMOUNT = 10
success = 0

async def make_request(session):
    async with session.post(url, json={
        "id": str(uuid4()),
        "payment_settings": "uah-card",
        "needed_amount": random.randint(500,5000),
        "user_uid": "1234567890",
        "webhook": "https://cpbotmv.online/bot/floawlRespond.php"
    }, headers=headers) as response:
        data = await response.json()
        if response.status in [200, 201]:
            global success
            success += 1
            print(data)
        else:
            print(f"Request failed with status {response.status}, {data}")


async def main():
    while True:
        global success
        async with aiohttp.ClientSession() as session:
            tasks = [make_request(session) for _ in range(AMOUNT)]
            await asyncio.gather(*tasks)
        print(f"Sent: {success}/{AMOUNT}")

        time.sleep(3)
        success = 0

asyncio.run(main())