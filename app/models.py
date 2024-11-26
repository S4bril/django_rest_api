from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    date_of_birth = models.DateTimeField()
    bio = models.TextField(max_length=500)
    friends = models.ManyToManyField("self", blank=True)
    email = models.EmailField(("email address"), blank=False, unique=True)

    def __str__(self):
        return f"{self.username}"