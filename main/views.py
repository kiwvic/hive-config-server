import asyncio
from .services.utils import *
from datetime import datetime, timedelta
from django.shortcuts import render
from django.http import HttpResponse
from .models import Farm, Rig
from .services.farm import *


def index(req):
    if req.method == "POST":
        res = json.loads(req.body)
        print(res)

        if not sender_is_rig(req, int(res["FarmId"])):
            return HttpResponse(status=404)

        farm_object, _ = Farm.objects.get_or_create(id=res["FarmId"])
        
        try:
            rig_obj = Rig.objects.get(id=int(res["RigId"]))
            rig_obj.last_request = datetime.now()
            rig_obj.pools = " ".join(res["Pools"])
            rig_obj.wallets = " ".join(res["Wallets"])
            rig_obj.config_url = res["ConfigUrl"]
            rig_obj.err_code = res["ErrCode"]
        except:
            rig_obj = Rig.objects.create(
                id=int(res["RigId"]), 
                farm_id=farm_object, 
                pools=" ".join(res["Pools"]),
                wallets=" ".join(res["Wallets"]),
                config_url=res["ConfigUrl"],
                err_code=res["ErrCode"],
                last_request=datetime.now()
            )
        rig_obj.save()

        return HttpResponse(status=200)
        
    elif req.method == "GET":
        farms_data = get_farms_info()

        asyncio.run(add_rigs_to_farms(farms_data))

        remove_inactive(farms_data)  # TODO add scheduled task

        fill_farm_data(farms_data)

        return render(req, 'main/index.html', farms_data)
