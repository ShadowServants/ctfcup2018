from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class InviteCode(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    code = models.CharField(max_length=16)


class Document(models.Model):
    title = models.CharField(max_length=100)
    text = models.TextField()
    rendered_file = models.FileField(upload_to='rendered_docs/', null=True)
    owner = models.ForeignKey(Group, on_delete=models.CASCADE)

    def to_elastic(self):
        return {"text": self.text, "title": self.title, "group_id": self.owner_id, "id": self.id}