from __future__ import annotations

import asyncio

from crm_api import CRMApiClient


async def main() -> None:
    # Pass credentials explicitly. SDK does not read .env or os.environ.
    async with CRMApiClient(
        base_url="https://your-crm.example",  # API base URL
        staff_id=123,                           # your staff ID
        service_token="YOUR_SERVICE_TOKEN",   # service token
    ) as client:
        user = await client.get_user(7014133383)
        print(user)


if __name__ == "__main__":
    asyncio.run(main())

