from .utils import get_farms_info, get_rigs_info, get_client_ip, hash_convert
from datetime import datetime, timedelta
from django.shortcuts import render
from django.http import HttpResponse
from .models import Farm, Rig
import pytz
from json import load

utc=pytz.UTC
__CONFIG_FILE = load(open("./main/config.json"))
LAST_REQUEST_WARNING_TIME = timedelta(minutes=__CONFIG_FILE["last_request_warning_time"])

def index(req):
    if req.method == "POST":
        farm_id, rig_id, pools, wallets, config_url = req.body.decode("utf-8").split(",")

        # sender is an actual rig?
        rig_ips = []
        for r in get_rigs_info(int(farm_id))["data"]:
            if "remote_address" in r:
                rig_ips.append(r["remote_address"]["ip"])
        
        if get_client_ip(req) not in rig_ips:
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

        for farm in farms_data["data"]:
            farm["rigs"] = get_rigs_info(farm["id"])["data"]

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
                    rig["hashrate_sum"] = [{"algo": algo, "hashrate_sum": int(s)} for algo, s in zip(rig_algos, rig_hashrate_sum)]

                # warning if rig did not make requests in LAST_REQUEST_WARNING_TIME
                rig["last_request"] = rig_object.last_request
                rig["last_request_warning"] = (utc.localize(datetime.now()) - rig_object.last_request) > LAST_REQUEST_WARNING_TIME            

                rig["pools"] = rig_object.pools

                rig["wallets"] = rig_object.wallets

                # will display text after farm name if last_request_warning
                if rig["last_request_warning"] and "last_request_warning" in farm:
                    if not farm["last_request_warning"]:
                        farm["last_request_warning"] = True
                else:
                    farm["last_request_warning"] = rig["last_request_warning"]
                
                rig["config_type"] = __CONFIG_FILE["configs"][rig_object.config_url]

        return render(req, 'main/index.html', farms_data)
