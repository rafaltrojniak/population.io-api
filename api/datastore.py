import os, time
import pandas as pd
from django.conf import settings


class HDF5DataStore(object):
    """ Alternative data store implementation, based on the HDF5 format. Potentially faster than the current CSV/filesystem-based implementation, but
        had occasional inexplicable HDF5ExtErrors with unclear causes.
    """

    def __init__(self, storeFilename=settings.DATA_STORE_PATH):
        # prepare the filesystem cache
        self._store = pd.HDFStore(storeFilename, mode='a' if settings.DATA_STORE_WRITABLE else 'r', complevel=9, complib='blosc')

        # if possible, initialize from data store, otherwise read the CSVs
        if self._store.get_node('data') and self._store.get_node('life_expectancy_ages'):
            self.initialize()
        else:
            print 'Base data not found in the data store, reading from CSV...'
            self.readCSVs()

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
        if settings.DATA_STORE_WRITABLE:
            self.storeExtrapolationTable(sex, country, table)
        return table

    def getOrGenerateExtrapolationTable(self, sex, country):
        key = self._buildTableKey(sex, country)
        if self._store.get_node(key):
            return self.retrieveExtrapolationTable(sex, country)
        else:
            return self.generateExtrapolationTable(sex, country)


class CSVDataStore(object):
    """ Data store implementation based on various CSVs with predefined filenames in a local filesystem path.
    """

    def __init__(self, storeFilename=settings.DATA_STORE_PATH):
        print 'Reading base data CSVs...'
        self.readCSVs()

    def registerTableBuilder(self, builder):
        self._extrapolation_table_builder = builder

    def readCSVs(self):
        start = time.clock()
        self.data = pd.read_csv(settings.CSV_POPULATION_PATH)
        self.life_expectancy_ages = pd.read_csv(settings.CSV_LIFE_EXPECTANCY_PATH)
        self.countries = pd.unique(self.data.Location).tolist()
        print 'Parsed CSVs in %.02f seconds' % (time.clock()-start)

    def __getitem__(self, item):
        sex, country = item
        return self.getOrGenerateExtrapolationTable(sex, country)

    def _buildTableKey(self, sex, country):
        return '%s/%s' % (sex, country)

    def _buildExtrapolationTableFilename(self, sex, country):
        key = '%s-%s' % (sex, country.replace(' ', '_'))
        return os.path.join(settings.DATA_STORE_PATH, key + '.pkl')

    def storeExtrapolationTable(self, sex, country, table):
        start = time.clock()
        table.to_pickle(self._buildExtrapolationTableFilename(sex, country))
        print 'Stored extrapolation table for (%s, %s) in %.02f seconds' % (sex, country, time.clock()-start)

    def retrieveExtrapolationTable(self, sex, country):
        start = time.clock()
        table = pd.read_pickle(self._buildExtrapolationTableFilename(sex, country))
        print 'Retrieved extrapolation table for (%s, %s) in %.02f seconds' % (sex, country, time.clock()-start)
        return table

    def generateExtrapolationTable(self, sex, country):
        start = time.clock()
        print 'Generating extrapolation table for (%s, %s)...' % (sex, country)
        table = self._extrapolation_table_builder(sex, country)
        print 'Generated extrapolation table for (%s, %s) in %.02f seconds' % (sex, country, time.clock()-start)
        if settings.DATA_STORE_WRITABLE:
            self.storeExtrapolationTable(sex, country, table)
        return table

    def getOrGenerateExtrapolationTable(self, sex, country):
        path = self._buildExtrapolationTableFilename(sex, country)
        if os.path.exists(path):
            return self.retrieveExtrapolationTable(sex, country)
        else:
            return self.generateExtrapolationTable(sex, country)


# the central data store instance we're gonna use
dataStore = CSVDataStore()
