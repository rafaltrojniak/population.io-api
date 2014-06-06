import time
from django.core.management.base import BaseCommand
from django.conf import settings
from api.datastore import dataStore


class Command(BaseCommand):
    args = ''
    help = 'Regenerates all extrapolation tables'

    def handle(self, *args, **kwargs):
        # it's important to import this to register the table builder with the data store
        import api.algorithms

        # we certainly don't want to cache 25 GiB of tables in memory
        settings.CACHE_TABLES_IN_MEMORY = False

        self.stdout.write('This command will regenerate all the extrapolation tables. Existing tables will be overwritten.')
        self.stdout.write('Please note that you should have about 25 GiB of free disk space.')

        self.stdout.write('Rereading CSV to make sure we have the latest version of the dataset...')
        dataStore.readCSVs()

        sexes = api.algorithms.SEXES.keys()
        countries = dataStore.countries
        totalCount = len(sexes)*len(countries)
        self.stdout.write('Regenerating %i extrapolation tables... this will take a while!' % totalCount)

        counter = 0
        calculationTimes = []
        for sex in sexes:
            for region in countries:
                start = time.clock()
                table = dataStore.generateExtrapolationTable(sex, region)
                table = None   # delete from memory immediately
                calculationTimes.append(time.clock() - start)
                counter += 1
                avgCalcTime = sum(calculationTimes)/len(calculationTimes)
                estimation = max(1.0, (totalCount - counter) * avgCalcTime / 60)
                self.stdout.write('Generated %i / %i tables, estimating %i minutes left.' % (counter, totalCount, estimation))
