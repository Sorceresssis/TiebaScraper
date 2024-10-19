import asyncio
from dataclasses import dataclass
from typing import TypedDict, List
from urllib.parse import urlparse, parse_qs

import aiohttp
import orjson


@dataclass
class N0099TbmV1PostsPage(TypedDict):
    has_more: int
    has_prev: int
    tnum: int
    page_size: int
    current_page: int
    total_page: int
    total_num: int
    new_total_page: int
    offset: int
    req_num: int
    pnum: int


@dataclass
class N0099TbmV1PostsPostItem(TypedDict):
    id: int
    floor: int
    content: List


@dataclass
class N0099TbmV1Posts(TypedDict):
    page: N0099TbmV1PostsPage
    post_list: List[N0099TbmV1PostsPostItem]


async def get_custom_emoticon_src(
        tid: int,
        pn: int,
        pid: int,
        floor: int,
        content_idx: int,
):
    async with aiohttp.ClientSession() as session:
        async with session.get(
                f"https://n0099.net/tbm/v1/client_tester.php?type=replies&tid={tid}&pn={pn}&client_version=12.62.1.0"
        ) as response:
            html = await response.text()
            res_data: N0099TbmV1Posts = orjson.loads(html)

            if "page" not in res_data:
                raise Exception("page not in resData")

            # 找的post
            for post in res_data["post_list"]:
                if not (post["id"] == pid and post["floor"] == floor):
                    continue

                if len(post["content"]) > content_idx:
                    content = post["content"][content_idx]
                    if "cdn_src" in content:
                        return extract_custom_emoticon_url(content["cdn_src"])
                    else:
                        return None
                else:
                    return None


def extract_custom_emoticon_url(raw_url: str) -> str | None:
    url = urlparse(raw_url)
    if url.hostname == "c.tieba.baidu.com" and url.path == "/c/p/img":
        query_params = parse_qs(url.query)
        return query_params.get("src", [None])[0]

    return raw_url


async def main():
    print(await get_custom_emoticon_src(2428664072, 6, 37592674736, 108, 0))


if __name__ == "__main__":
    asyncio.run(main())
