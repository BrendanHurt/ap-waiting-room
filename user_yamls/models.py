from django.db import models
from users.models import users

# Create your models here.
class user_yamls(models.Model):
    user_id = models.ForeignKey(users, on_delete=models.CASCADE)
    yaml_file = models.FileField()
    slot = models.CharField(max_length=16, default="Default Slot")
    game_name = models.CharField(max_length=50, default="Default Game Name")
    description = models.CharField(max_length=1000, null=True)
    last_edited = models.DateField(auto_now = True)

    def __str__(self):
        return 'yup'