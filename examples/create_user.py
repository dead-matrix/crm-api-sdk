from __future__ import annotations

import asyncio

from crm_api import CRMApiClient, CreateUserInput


async def main() -> None:
    async with CRMApiClient(
        base_url="https://your-crm.example",
        staff_id=123,
        service_token="YOUR_SERVICE_TOKEN",
    ) as client:
        payload = CreateUserInput(
            user_id=7014133383,
            full_name="John Doe",
            username="johndoe",
            bot_id=1
        )
        res = await client.create_user(payload)
        print(res)


if __name__ == "__main__":
    asyncio.run(main())

