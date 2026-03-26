from django.db import models

# Create your models here.
class users(models.Model):
    name = models.CharField(max_length = 32)
    email = models.CharField(max_length = 200)
    status = models.CharField(max_length = 32)

    def __str__(self):
        return f"{self.name}, {self.email}, {self.status}"