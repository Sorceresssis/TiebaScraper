import aiotieba as tb
from tieba_property import BDUSS


async def get_forum(fname_or_fid: str | int):
    async with tb.Client(BDUSS) as client:
        return await client.get_forum(fname_or_fid)


async def get_forum_detail(fname_or_fid: str | int):
    async with tb.Client(BDUSS) as client:
        return await client.get_forum_detail(fname_or_fid)


async def get_posts(tid: int, pn=1):
    async with tb.Client(BDUSS) as client:
        return await client.get_posts(tid, pn, with_comments=True)


async def get_comments(tid: int, pid: int, pn=1):
    async with tb.Client(BDUSS) as client:
        return await client.get_comments(tid, pid, pn)


async def get_user_info(user_id: str | int):
    async with tb.Client(BDUSS) as client:
        return await client.get_user_info(user_id)
