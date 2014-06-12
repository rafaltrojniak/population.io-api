import os, time
import pandas as pd
from django.conf import settings



class DataStore(object):

    SEXES = {'male': 'PopMale', 'female': 'PopFemale', 'unisex': 'PopTotal',}   # FIXME: only temporary needed for old data file

    def __init__(self, storeFilename=settings.DATA_STORE_PATH):
        # prepare the filesystem cache
        self._store = pd.HDFStore(storeFilename, mode='a' if settings.DATA_STORE_WRITABLE else 'r', complevel=9, complib='blosc')

        # if possible, initialize from data store, otherwise read the CSVs
        if self._store.get_node('data') and self._store.get_node('life_expectancy_ages'):
            self.initialize()
        else:
            print 'Base data not found in the data store, reading from CSV...'
            self.readCSVs()

        # create two dimensional lookup table for extrapolation tables, based on (sex, country) tuples
        self.extrapolation_tables = {}

    def registerTableBuilder(self, builder):
        self._extrapolation_table_builder = builder

    def initialize(self):
        start = time.clock()
        self.data = self._store.get('data')
        self.life_expectancy_ages = self._store.get('life_expectancy_ages')
        self.countries = pd.unique(self.data.Location).tolist()
        print 'Initialized data store in %.02f seconds' % (time.clock()-start)

    def readCSVs(self):
        start = time.clock()
        self.data = pd.read_csv(settings.CSV_POPULATION_PATH)
        self.life_expectancy_ages = pd.read_csv(settings.CSV_LIFE_EXPECTANCY_PATH)
        self.countries = pd.unique(self.data.Location).tolist()
        self._store.put('data', self.data)
        self._store.put('life_expectancy_ages', self.life_expectancy_ages)
        print 'Parsed CSVs in %.02f seconds' % (time.clock()-start)

    def __getitem__(self, item):
        sex, country = item
        return self.getOrGenerateExtrapolationTable(sex, country)

    def _buildTableKey(self, sex, country):
        return '%s/%s' % (sex, country)

    def storeExtrapolationTable(self, sex, country, table):
        start = time.clock()
        self._store.put(self._buildTableKey(sex, country), table)
        print 'Stored extrapolation table for (%s, %s) in %.02f seconds' % (sex, country, time.clock()-start)

    def retrieveExtrapolationTable(self, sex, country):
        start = time.clock()
        table = self._store.get(self._buildTableKey(sex, country))
        print 'Retrieved extrapolation table for (%s, %s) in %.02f seconds' % (sex, country, time.clock()-start)
        return table

    def generateExtrapolationTable(self, sex, country):
        start = time.clock()
        table = self._extrapolation_table_builder(sex, country)
        print 'Generated extrapolation table for (%s, %s) in %.02f seconds' % (sex, country, time.clock()-start)
        self.storeExtrapolationTable(sex, country, table)
        return table

    def getOrGenerateExtrapolationTable(self, sex, country):
        if (sex, country) in self.extrapolation_tables:
            return self.extrapolation_tables[(sex, country)]

        key = self._buildTableKey(sex, country)
        if self._store.get_node(key):
            table = self.retrieveExtrapolationTable(sex, country)
        else:
            table = self.generateExtrapolationTable(sex, country)
        if settings.CACHE_TABLES_IN_MEMORY:
            self.extrapolation_tables[(sex, country)] = table
        return table

dataStore = DataStore()
