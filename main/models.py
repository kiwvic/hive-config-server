from django.db import models

# Create your models here.

class Farm(models.Model):
    pass


class Rig(models.Model):
    farm_id = models.ForeignKey(Farm, on_delete=models.CASCADE)
    last_request = models.DateTimeField()
    pools = models.CharField(max_length=200, null=True, blank=True)
    wallets = models.CharField(max_length=200, null=True, blank=True)
    config_url = models.CharField(max_length=200, null=True, blank=True)
    err_code = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.farm_id} {self.last_request} {self.pools} {self.wallets} {self.config_url} {self.err_code}"