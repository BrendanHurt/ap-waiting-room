from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class UserAccount(models.Model):
    name = models.CharField(max_length = 32)
    email = models.CharField(max_length = 200)
    status = models.CharField(max_length = 32)

    def __str__(self):
        return f"{self.name}, {self.email}, {self.status}"