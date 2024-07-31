import asyncio
from src import consumers


async def run_async_application(func):
    await asyncio.gather(*func)


if __name__ == "__main__":
    asyncio.run(run_async_application(consumers))
