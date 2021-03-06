from .utils import *
import pytz
from datetime import datetime, timedelta
from json import load

utc=pytz.UTC
__CONFIG_FILE = load(open("./main/config.json"))  # TODO
LAST_REQUEST_WARNING_TIME = timedelta(minutes=__CONFIG_FILE["last_request_warning_time"])
REMOVE_FROM_TABLE_TIME = timedelta(minutes=__CONFIG_FILE["remove_from_table_time"])

class Errors:
    NO_REQUESTS = -1
    NO_COIN = -2
    ALGT5 = -3
    MAINT_MODE = -4
    MINER_TURNED_OFF = -5

ErrorsNames = {
    Errors.NO_REQUESTS: "NO_REQUESTS",
    Errors.NO_COIN: "NO_COIN",
    Errors.ALGT5: "AL > 5",
    Errors.MAINT_MODE: "Maint. Mode",
    Errors.MINER_TURNED_OFF: "Miner Off"
}


def add_hashrate(rig_algos, rig_hashrate_sum, rig):
    if "miners_stats" in rig:
        for hs in rig["miners_stats"]["hashrates"]:
            rig_algos.append(hs["algo"])
            rig_hashrate_sum.append(hash_convert(sum(hs["hashes"])))
        rig["hashrate_sum"] = [{"algo": algo, "hashrate_sum": s} for algo, s in zip(rig_algos, rig_hashrate_sum)]

def add_warnings(rig, rig_object):
    rig["warnings"] = list()
    last_request_warning = (utc.localize(datetime.now()) - rig_object.last_request) > LAST_REQUEST_WARNING_TIME and rig["stats"]["online"]
    
    if last_request_warning and rig["stats"]["online"]:
        rig["warnings"].append(ErrorsNames[Errors.NO_REQUESTS])

    if rig_object.err_code in ErrorsNames and rig["stats"]["online"]:
        rig["warnings"].append(ErrorsNames[rig_object.err_code])

def add_pools(rig, rig_object):
    rig["pools"] = ";\n".join(rig_object.pools.split())

def add_wallets(rig, rig_object):
    rig["wallets"] = ";\n".join(rig_object.wallets.split())

def add_config_type(rig, rig_object):
    if str(rig_object.config_url) in __CONFIG_FILE["configs"]:
        rig["config_type"] = __CONFIG_FILE["configs"][rig_object.config_url]
