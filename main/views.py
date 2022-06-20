import pytz
import asyncio
from .utils import *
from datetime import datetime, timedelta
from django.shortcuts import render
from django.http import HttpResponse
from .models import Farm, Rig
from json import load

utc=pytz.UTC
__CONFIG_FILE = load(open("./main/config.json"))
LAST_REQUEST_WARNING_TIME = timedelta(minutes=__CONFIG_FILE["last_request_warning_time"])
REMOVE_FROM_TABLE_TIME = timedelta(minutes=__CONFIG_FILE["remove_from_table_time"])


def index(req):
    if req.method == "POST":
        farm_id, rig_id, pools, wallets, config_url = req.body.decode("utf-8").split(",")

        if not sender_is_rig(req, int(farm_id)):
            return HttpResponse(status=404)

        farm_object, _ = Farm.objects.get_or_create(id=int(farm_id))
        
        try:
            rig_obj = Rig.objects.get(id=int(rig_id))
            rig_obj.last_request = datetime.now()
            rig_obj.pools = pools
            rig_obj.wallets = wallets
            rig_obj.config_url = config_url
        except:
            rig_obj = Rig.objects.create(
                id=int(rig_id), 
                farm_id=farm_object, 
                pools=pools,
                wallets=wallets,
                config_url=config_url,
                last_request=datetime.now()
            )
        rig_obj.save()

        return HttpResponse(status=200)
        
    elif req.method == "GET":
        farms_data = get_farms_info()

        asyncio.run(add_rigs_to_farms(farms_data))

        # __remove_inactive(farms_data)  # TODO add scheduled task

        for farm in farms_data["data"]:
            if "hashrates_by_coin" in farm:
                for h in farm["hashrates_by_coin"]:
                    h["hashrate"] = hash_convert(h["hashrate"])
            
            for rig in farm["rigs"]:
                rig_algos = []
                rig_hashrate_sum = []

                try:
                    rig_object = Rig.objects.get(id=rig["id"])
                except:
                    continue

                # hashrate column
                if "miners_stats" in rig:
                    for hs in rig["miners_stats"]["hashrates"]:
                        rig_algos.append(hs["algo"])
                        rig_hashrate_sum.append(hash_convert(sum(hs["hashes"])))
                    rig["hashrate_sum"] = [{"algo": algo, "hashrate_sum": s} for algo, s in zip(rig_algos, rig_hashrate_sum)]

                # warning if rig did not make requests in LAST_REQUEST_WARNING_TIME
                rig["last_request"] = rig_object.last_request
                rig["last_request_warning"] = (utc.localize(datetime.now()) - rig_object.last_request) > LAST_REQUEST_WARNING_TIME            

                rig["pools"] = ";\n".join(rig_object.pools.split())

                rig["wallets"] = ";\n".join(rig_object.wallets.split())

                # will display text after farm name if last_request_warning
                if rig["last_request_warning"] and "last_request_warning" in farm:
                    if not farm["last_request_warning"]:
                        farm["last_request_warning"] = True
                else:
                    farm["last_request_warning"] = rig["last_request_warning"]
                
                rig["config_type"] = __CONFIG_FILE["configs"][rig_object.config_url]
        return render(req, 'main/index.html', farms_data)


def __get_inactive_rigs():
    return Rig.objects.filter(last_request__lte=utc.localize(datetime.now())- REMOVE_FROM_TABLE_TIME)

def __remove_inactive(farms_data):
    rigs_to_remove = __get_inactive_rigs()

    if rigs_to_remove:
        actual_data = dict()
        for farm in farms_data["data"]:
            actual_rigs = [i["id"] for i in get_rigs_info(farm["id"])["data"]]
            actual_data[farm["id"]] = actual_rigs

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
