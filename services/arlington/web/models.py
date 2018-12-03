from django.contrib.auth.models import Group, User
from django.db import models


class Draft(models.Model):
    title = models.CharField(max_length=100)
    text = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
