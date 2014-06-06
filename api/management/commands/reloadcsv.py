from django.core.management.base import BaseCommand
from api.datastore import dataStore


class Command(BaseCommand):
    args = ''
    help = 'Reloads the CSV source data files'

    def handle(self, *args, **kwargs):
        dataStore.readCSVs()
