from django.apps import AppConfig
from django.db.models.signals import post_save


class GroupsConfig(AppConfig):
    name = 'groups'
