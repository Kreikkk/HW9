from sys import argv


def parse_file(filename):
    with open(filename, 'r') as f:
        urls = f.readlines()
    urls = [url.replace('\n', '') for url in urls]

    return urls


def parse_CL():
    params = dict(map(lambda x: x.lstrip('--').split('='), argv[1:]))
    params = {k: v for k, v in params.items()}

    return params


# async def main():
#     urls = parse_file(PARAMS.get('f', 'urls.txt'))
#     async with aiohttp.ClientSession() as session:
#         tasks = [asyncio.create_task(fetch(url, session)) for url in urls]
#         await gather_with_concurrency(int(PARAMS.get('c', 1)), *tasks)


# async def fetch(url, session):
#     async with session.get(url) as resp:
#         data = await resp.read()
#         print(url)


# async def gather_with_concurrency(n, *tasks):
#     semaphore = asyncio.Semaphore(n)

#     async def sem_task(task):
#         async with semaphore:
#             return await task
#     return await asyncio.gather(*(sem_task(task) for task in tasks))
