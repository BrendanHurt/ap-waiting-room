from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Yaml(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    slot_name = models.CharField(max_length=16, default="Default Slot")
    game_name = models.CharField(max_length=50, default="Default Game Name")
    description = models.CharField(max_length=1000, null=True)
    game_options = models.CharField(default="EMPTY SETTINGS")
    last_edited = models.DateField(auto_now = True)

    def __str__(self):
        return f"{self.slot}\n{self.game_name}\n{self.description}\n\n{self.game_options}"