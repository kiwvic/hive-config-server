from .utils import *
from ..models import Rig, Farm
from .rig import *


def fill_farm_data(farms_data):
    all_hashrates = dict()
    for farm in farms_data["data"]:
        farm["warnings"] = list()
        
        __add_hashrates(all_hashrates, farm)

        __add_hashrate(farm)
        
        for rig in farm["rigs"]:
            rig_algos = []
            rig_hashrate_sum = []

            try:
                rig_object = Rig.objects.get(id=rig["id"])
            except:
                continue

            add_hashrate(rig_algos, rig_hashrate_sum, rig)

            rig["last_request"] = rig_object.last_request

            add_warnings(rig, rig_object)

            __add_warnings(rig, farm)

            add_pools(rig, rig_object)

            add_wallets(rig, rig_object)

            add_config_type(rig, rig_object)

    __fill_all_hashrates(all_hashrates, farms_data)    



def __add_hashrates(all_hashrates, farm):
    if "hashrates" in farm:
        for h in farm["hashrates"]:
            if h["algo"] in all_hashrates:
                all_hashrates[h["algo"]] = all_hashrates[h["algo"]] + h["hashrate"]
            else:
                all_hashrates[h["algo"]] = h["hashrate"]

def __fill_all_hashrates(all_hashrates, farms_data):
    for h in all_hashrates:
        all_hashrates[h] = hash_convert(all_hashrates[h])
    farms_data["all_hashrates"] = [{"algo": i, "hashrate": j} for i, j in all_hashrates.items()]

def __add_hashrate(farm):
    if "hashrates_by_coin" in farm:
        for h in farm["hashrates_by_coin"]:
            h["hashrate"] = hash_convert(h["hashrate"])

def __add_warnings(rig, farm):
    for w in rig["warnings"]:
        if w not in farm["warnings"]:
            farm["warnings"].append(w)

def __get_inactive_rigs():
    return Rig.objects.filter(last_request__lte=utc.localize(datetime.now())- REMOVE_FROM_TABLE_TIME)

def remove_inactive(farms_data):
    rigs_to_remove = __get_inactive_rigs()

    if rigs_to_remove:
        actual_data = dict()
        for farm in farms_data["data"]:
            actual_data[farm["id"]] = [i["id"] for i in farm["rigs"]]

        farms_local = [i.farm_id.id for i in rigs_to_remove]
        farms_to_remove = set(farms_local).difference(set(actual_data.keys()))

        if farms_to_remove:
            for farm_id in farms_to_remove:
                if farm_id not in actual_data:
                    Farm.objects.get(id=farm_id).delete()
            rigs_to_remove = __get_inactive_rigs()
        
        if rigs_to_remove:
            for rig in rigs_to_remove:
                if rig.id not in actual_data[rig.farm_id.id]:
                    rig.delete()