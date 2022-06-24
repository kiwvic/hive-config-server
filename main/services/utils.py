from dotenv import load_dotenv
from django.conf import settings
import os
import urllib3
import json
import asyncio
import aiohttp

load_dotenv(str(settings.BASE_DIR) + "/.env")
__HIVE_TOKEN = os.getenv("HIVE_TOKEN")


def __get_info(url: str) -> dict:
    http = urllib3.PoolManager()
    req = http.request(
        "GET", 
        url,
        headers={
            "Authorization": f"Bearer {__HIVE_TOKEN}",
            "accept": "application/json"
        }
    )
    return json.loads(req.data.decode('utf-8'))

def get_farms_info() -> dict:
    url = "https://api2.hiveos.farm/api/v2/farms"
    return __get_info(url)

def get_rigs_info(farm_id: int) -> dict:
    url = f"https://api2.hiveos.farm/api/v2/farms/{farm_id}/workers"
    return __get_info(url)


def __get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def sender_is_rig(request, farm_id):
    rig_ips = []
    for r in get_rigs_info(int(farm_id))["data"]:
        if "remote_address" in r:
            rig_ips.append(r["remote_address"]["ip"])
    
    return __get_client_ip(request) in rig_ips


def hash_convert(kh: int) -> str:
    if kh // 1000_000_000:
        return f"{(kh / 1000_000_000):.{1}f}Th"
    elif kh // 1000_000:
        return f"{(kh / 1000_000):.{1}f}Gh"
    elif kh // 1000:
        return f"{(kh / 1000):.{1}f}Mh"
    else:
        return f"{kh}kh"


async def __add_rig_to_farm(session, url, farm):
    headers = {
        "Authorization": f"Bearer {__HIVE_TOKEN}",
        "accept": "application/json"
    }

    async with session.get(url, headers=headers) as r:
        farm["rigs"] = (await r.json())["data"]

async def add_rigs_to_farms(farms):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for farm in farms["data"]:
            url = f"https://api2.hiveos.farm/api/v2/farms/{farm['id']}/workers"
            tasks.append(asyncio.ensure_future(__add_rig_to_farm(session, url, farm)))
        
        await asyncio.gather(*tasks)