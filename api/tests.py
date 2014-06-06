from datetime import datetime, timedelta
from django.test import SimpleTestCase
from django.conf import settings
from rest_framework.test import APISimpleTestCase
settings.CACHE_TABLES_IN_MEMORY = True
from api.algorithms import worldPopulationRankByDate, dateByWorldPopulationRank, lifeExpectancy, populationCount
from api.datastore import dataStore
from api.exceptions import *





class TestWorldPopulationRankCalculation(SimpleTestCase):
    """
    Tests the world population rank calculation functions. All the reference values have been generated with the
    original R script (see modeling/R/).
    """

    DELTA = 1000000

    def test_regions(self):
        self.assertTrue(len(dataStore.countries) > 200)
        self.assertTrue('World' in dataStore.countries)
        self.assertTrue('Estonia' in dataStore.countries)
        self.assertTrue('Europe' in dataStore.countries)
        self.assertTrue('Reunion' in dataStore.countries)

    def test_byDate_today(self):
        self.assertAlmostEqual(56598000,   worldPopulationRankByDate('unisex', 'World', datetime(2013, 12, 31), datetime(2014,  6,  1)), delta=TestWorldPopulationRankCalculation.DELTA)
        self.assertAlmostEqual(2541178000, worldPopulationRankByDate('unisex', 'World', datetime(1993, 12,  6), datetime(2014,  6,  1)), delta=TestWorldPopulationRankCalculation.DELTA)
        self.assertAlmostEqual(4178250000, worldPopulationRankByDate('unisex', 'World', datetime(1980,  1,  1), datetime(2014,  6,  1)), delta=TestWorldPopulationRankCalculation.DELTA)
        self.assertAlmostEqual(5989238000, worldPopulationRankByDate('unisex', 'World', datetime(1960,  2, 29), datetime(2014,  6,  1)), delta=TestWorldPopulationRankCalculation.DELTA)
        self.assertAlmostEqual(7233264000, worldPopulationRankByDate('unisex', 'World', datetime(1920,  1,  1), datetime(2014,  6,  1)), delta=TestWorldPopulationRankCalculation.DELTA)

    def test_byDate_age(self):
        self.assertAlmostEqual(2541533000, worldPopulationRankByDate('unisex', 'World', datetime(1993, 12,  6), datetime(1993, 12,  6) + timedelta(days=7483)), delta=TestWorldPopulationRankCalculation.DELTA)
        self.assertAlmostEqual(1209918000, worldPopulationRankByDate('unisex', 'World', datetime(1993, 12,  6), datetime(1993, 12,  6) + timedelta(days=3650)), delta=TestWorldPopulationRankCalculation.DELTA)
        self.assertAlmostEqual(578344100,  worldPopulationRankByDate('unisex', 'World', datetime(1940,  5,  3), datetime(1940,  5,  3) + timedelta(days=3530)), delta=TestWorldPopulationRankCalculation.DELTA)
        self.assertAlmostEqual(217482,     worldPopulationRankByDate('unisex', 'World', datetime(1950,  1,  1), datetime(1950,  1,  1) + timedelta(days=0)),    delta=TestWorldPopulationRankCalculation.DELTA)

    def test_byDate_date(self):
        self.assertAlmostEqual(940947000,  worldPopulationRankByDate('unisex', 'World', datetime(1993, 12,  6), datetime(2001,  9, 11)), delta=TestWorldPopulationRankCalculation.DELTA)
        self.assertAlmostEqual(7198923000, worldPopulationRankByDate('unisex', 'World', datetime(1920,  1,  1), datetime(2014,  1,  1)), delta=TestWorldPopulationRankCalculation.DELTA)

    def test_byDate_invalidSex(self):
        self.assertRaises(InvalidSexError, worldPopulationRankByDate, 'INVALID', 'World', datetime(1980, 1, 1), datetime(2000, 1, 1))

    def test_byDate_invalidRegion(self):
        self.assertRaises(InvalidCountryError, worldPopulationRankByDate, 'unisex', 'THIS COUNTRY DOES NOT EXIST', datetime(1980, 1, 1), datetime(2000, 1, 1))

    def test_byDate_dobOutOfRange(self):
        self.assertRaises(BirthdateOutOfRangeError, worldPopulationRankByDate, 'unisex', 'World', datetime(1915, 1, 1), datetime(2000, 1, 1))
        self.assertRaises(BirthdateOutOfRangeError, worldPopulationRankByDate, 'unisex', 'World', datetime(2030, 1, 1), datetime(2000, 1, 1))

    def test_byDate_dateOutOfRange(self):
        self.assertRaises(CalculationDateOutOfRangeError, worldPopulationRankByDate, 'unisex', 'World', datetime(1945, 1, 1), datetime(1949, 1, 1))
        self.assertRaises(CalculationDateOutOfRangeError, worldPopulationRankByDate, 'unisex', 'World', datetime(1970, 1, 1), datetime(1960, 1, 1))

    def test_byDate_calculationTooWide(self):
        self.assertRaises(CalculationTooWideError, worldPopulationRankByDate, 'unisex', 'World', datetime(1930, 1, 1), datetime(2031, 1, 1))

    def test_byRank(self):
        self.assertEqual(datetime(2049,  3, 11), dateByWorldPopulationRank('unisex', 'World', datetime(1993, 12,  6), 7000000000))

    def test_lifeExpectancy(self):
        self.assertAlmostEqual(26.24, lifeExpectancy('unisex', 'World', datetime(2049, 3, 11), 55.3), places=0)
        self.assertAlmostEqual(99.99, lifeExpectancy('male', 'UK', datetime(1952, 3, 11), 55.0), places=0)

    def test_population(self):
        data = list(populationCount('Brazil', 18, 1980))
        self.assertEqual(1, len(data))
        self.assertEqual(2719710, data[0]['total'])
        data = list(populationCount('Brazil', 18))
        self.assertEqual(151, len(data))
        self.assertEqual(1980, data[30]['year'])
        self.assertEqual(2719710, data[30]['total'])



class TestViews(APISimpleTestCase):
    def testRankEndpointToday(self):
        # valid request
        self._testEndpoint('/wp-rank/1952-03-11/unisex/World/today/')
        # invalid value for sex
        self._testEndpoint('/wp-rank/1952-03-11/123/World/today/', expectErrorContaining='sex')
        # invalid value for country
        self._testEndpoint('/wp-rank/1952-03-11/unisex/123/today/', expectErrorContaining='country')

    def testRankEndpointAged(self):
        # valid request: days given
        self._testEndpoint('/wp-rank/1952-03-11/unisex/World/aged/123/',)
        # valid request: full offset string given
        self._testEndpoint('/wp-rank/1952-03-11/unisex/World/aged/12y34m56d/')
        # invalid offset
        self._testEndpoint('/wp-rank/1952-03-11/unisex/World/aged/5x/', expectErrorContaining='offset')

    # TODO: need a lot more of these, and for the other endpoints, too

    def testPopulationEndpoint(self):
        # valid request
        self._testEndpoint('/population/Brazil/18/')
        # valid request
        self._testEndpoint('/population/Brazil/18/1980/')
        # invalid age: string given
        self._testEndpoint('/population/Brazil/abc/1980/', expectErrorContaining='number')
        # invalid age: string given, without year
        self._testEndpoint('/population/Brazil/abc/', expectErrorContaining='number')
        # invalid year: string given
        self._testEndpoint('/population/Brazil/18/abc/', expectErrorContaining='number')

    def _testEndpoint(self, path, expectErrorContaining=None):
        response = self.client.get('/api/1.0' + path)
        if expectErrorContaining:
            self.assertEqual(response.status_code, 400)
            self.assertTrue(expectErrorContaining in response.data['detail'], 'Expected fragment "%s" in error message: %s' % (expectErrorContaining, response.data['detail']))
        else:
            self.assertEqual(response.status_code, 200)
