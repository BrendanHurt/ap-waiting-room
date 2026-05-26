from django.db import models
from django.utils.timezone import now

from django.contrib.auth.models import User
from user_yamls.models import Yaml

# Create your models here.
class Lobby(models.Model):
    host_id = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(default="Lobby")
    start_date = models.DateField(default=now)
    is_async = models.BooleanField(default=False)
    description = models.CharField(default="")


class Slot(models.Model):
    lobby_id = models.ForeignKey(Lobby, on_delete=models.CASCADE)
    slot_id = models.ForeignKey(Yaml, on_delete=models.CASCADE)