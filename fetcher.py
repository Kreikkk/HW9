import asyncio
import aiohttp

from sys import argv
from tools import parse_CL, parse_file

PARAMS = parse_CL()


async def fetch(url, session, lock):
    async with lock:
        async with session.get(url) as resp:
            data = await resp.read()
            print(url)


async def main():
    n_conn = int(PARAMS.get('c', 10))
    urls = parse_file(PARAMS.get('f', 'urls.txt'))

    lock = asyncio.Semaphore(n_conn)

    async with aiohttp.ClientSession() as session:
        tasks = [asyncio.create_task(fetch(url, session, lock)) for url in urls]
        await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(main())