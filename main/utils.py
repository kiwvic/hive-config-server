from dotenv import load_dotenv
import os
import urllib3
import json

load_dotenv()
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

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def hash_convert(kh: int) -> str:
    # ternary for prettier output (remove .0 if number is integer)
    if kh // 1000_000_000:
        return f"{kh / 1000_000_000}Th"
    elif kh // 1000_000:
        return f"{kh / 1000_000}Gh"
    elif kh // 1000:
        return f"{kh / 1000}Mh"
    else:
        return f"{kh}kh"