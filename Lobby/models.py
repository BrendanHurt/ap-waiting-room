from django.db import models
from django.utils.timezone import now

from users.models import users
from user_yamls.models import user_yamls

# Create your models here.
class Lobby(models.Model):
    host_id = models.ForeignKey(users, on_delete=models.CASCADE)
    name = models.CharField(default="Lobby")
    start_date = models.DateField(default=now)
    is_async = models.BooleanField(default=False)
    description = models.CharField(default="")


class LobbyConnection(models.Model):
    lobby_id = models.ForeignKey(Lobby, on_delete=models.CASCADE)
    player_yaml = models.ForeignKey(user_yamls, on_delete=models.CASCADE)