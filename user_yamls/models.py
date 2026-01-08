from django.db import models
from users.models import users

# Create your models here.
class user_yamls(models.Model):
    user_id = models.ForeignKey(users, on_delete=models.CASCADE)
    yaml_file = models.FileField()
    last_edited = models.DateField(auto_now = True)