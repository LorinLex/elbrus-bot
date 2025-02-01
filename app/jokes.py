from copy import copy
from dataclasses import dataclass
import json
from random import shuffle
from typing import Any, Callable
import aiohttp
import xml.etree.ElementTree as ET


@dataclass
class Api:
    source: str
    url: str
    parser: Callable[[str], str | None]


def parser_shortiki(raw: str) -> str | None:
    json_obj: list[dict[str, Any]] = json.loads(raw)
    return (json_obj[0]).get("content")


def parser_rzhunemogu(raw: str) -> str | None:
    tree = ET.fromstring(raw)
    content = tree.find("content")
    if content is None:
        return None
    return content.text


api_list: list[Api] = [
    Api(
        source="shortiki.com",
        url="http://shortiki.com/export/api.php?"
            "format=json&type=random&amount=1",
        parser=parser_shortiki
    ),
    Api(
        source="rzhunemogu.ru (18+)",
        url="http://rzhunemogu.ru/Rand.aspx?CType=11",
        parser=parser_rzhunemogu
    ),
    Api(
        source="rzhunemogu.ru",
        url="http://rzhunemogu.ru/Rand.aspx?CType=1",
        parser=parser_rzhunemogu
    ),
]


async def get_joke():
    local_api_list = copy(api_list)
    shuffle(local_api_list)

    async with aiohttp.ClientSession() as session:
        for api in local_api_list:
            async with session.get(api.url) as responce:
                if responce.status != 200:
                    continue

                responce_raw = await responce.text()

                joke = api.parser(responce_raw)
                if joke:
                    return (api.source, joke)

    return (None, None)
