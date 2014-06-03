from django.test import SimpleTestCase
from datetime import datetime, timedelta

from api.algorithms import WorldPopulationRankCalculator
from api.exceptions import *



class TestWorldPopulationRankCalculation(SimpleTestCase):
    """
    Tests the world population rank calculation functions. All the reference values have been generated with the
    original R script (see modeling/R/).
    """

    DELTA = 1000000

    @classmethod
    def setUpClass(cls):
        cls.sut = WorldPopulationRankCalculator()
        cls.sut.readCSV()
        cls.sut.generateExtrapolationTable('unisex', 'WORLD')

    def test_regions(self):
        self.assertTrue(len(self.sut.REGIONS) > 200)
        self.assertTrue('WORLD' in self.sut.REGIONS)
        self.assertTrue('Estonia' in self.sut.REGIONS)
        self.assertTrue('EUROPE' in self.sut.REGIONS)
        self.assertTrue('R\xe9union' in self.sut.REGIONS)   # TODO: currently fails because latin1-encoded region names have been disabled

    def test_byDate_today(self):
        self.assertAlmostEqual(56598000,   self.sut.worldPopulationRankByDate('unisex', 'WORLD', datetime(2013, 12, 31), datetime(2014,  6,  1)), delta=TestWorldPopulationRankCalculation.DELTA)
        self.assertAlmostEqual(2541178000, self.sut.worldPopulationRankByDate('unisex', 'WORLD', datetime(1993, 12,  6), datetime(2014,  6,  1)), delta=TestWorldPopulationRankCalculation.DELTA)
        self.assertAlmostEqual(4178250000, self.sut.worldPopulationRankByDate('unisex', 'WORLD', datetime(1980,  1,  1), datetime(2014,  6,  1)), delta=TestWorldPopulationRankCalculation.DELTA)
        self.assertAlmostEqual(5989238000, self.sut.worldPopulationRankByDate('unisex', 'WORLD', datetime(1960,  2, 29), datetime(2014,  6,  1)), delta=TestWorldPopulationRankCalculation.DELTA)
        self.assertAlmostEqual(7233264000, self.sut.worldPopulationRankByDate('unisex', 'WORLD', datetime(1920,  1,  1), datetime(2014,  6,  1)), delta=TestWorldPopulationRankCalculation.DELTA)

    def test_byDate_age(self):
        self.assertAlmostEqual(2541533000, self.sut.worldPopulationRankByDate('unisex', 'WORLD', datetime(1993, 12,  6), datetime(1993, 12,  6) + timedelta(days=7483)), delta=TestWorldPopulationRankCalculation.DELTA)
        self.assertAlmostEqual(1209918000, self.sut.worldPopulationRankByDate('unisex', 'WORLD', datetime(1993, 12,  6), datetime(1993, 12,  6) + timedelta(days=3650)), delta=TestWorldPopulationRankCalculation.DELTA)
        self.assertAlmostEqual(578344100,  self.sut.worldPopulationRankByDate('unisex', 'WORLD', datetime(1940,  5,  3), datetime(1940,  5,  3) + timedelta(days=3530)), delta=TestWorldPopulationRankCalculation.DELTA)
        self.assertAlmostEqual(217482,     self.sut.worldPopulationRankByDate('unisex', 'WORLD', datetime(1950,  1,  1), datetime(1950,  1,  1) + timedelta(days=0)),    delta=TestWorldPopulationRankCalculation.DELTA)

    def test_byDate_date(self):
        self.assertAlmostEqual(940947000,  self.sut.worldPopulationRankByDate('unisex', 'WORLD', datetime(1993, 12,  6), datetime(2001,  9, 11)), delta=TestWorldPopulationRankCalculation.DELTA)
        self.assertAlmostEqual(7198923000, self.sut.worldPopulationRankByDate('unisex', 'WORLD', datetime(1920,  1,  1), datetime(2014,  1,  1)), delta=TestWorldPopulationRankCalculation.DELTA)

    def test_byDate_invalidSex(self):
        self.assertRaises(InvalidSexError, self.sut.worldPopulationRankByDate, 'INVALID', 'WORLD', datetime(1980, 1, 1), datetime(2000, 1, 1))

    def test_byDate_invalidRegion(self):
        self.assertRaises(InvalidRegionError, self.sut.worldPopulationRankByDate, 'unisex', 'THIS COUNTRY DOES NOT EXIST', datetime(1980, 1, 1), datetime(2000, 1, 1))

    def test_byDate_dobOutOfRange(self):
        self.assertRaises(BirthdateOutOfRangeError, self.sut.worldPopulationRankByDate, 'unisex', 'WORLD', datetime(1915, 1, 1), datetime(2000, 1, 1))
        self.assertRaises(BirthdateOutOfRangeError, self.sut.worldPopulationRankByDate, 'unisex', 'WORLD', datetime(2030, 1, 1), datetime(2000, 1, 1))

    def test_byDate_dateOutOfRange(self):
        self.assertRaises(CalculationDateOutOfRangeError, self.sut.worldPopulationRankByDate, 'unisex', 'WORLD', datetime(1945, 1, 1), datetime(1949, 1, 1))
        self.assertRaises(CalculationDateOutOfRangeError, self.sut.worldPopulationRankByDate, 'unisex', 'WORLD', datetime(1970, 1, 1), datetime(1960, 1, 1))

    def test_byDate_calculationTooWide(self):
        self.assertRaises(CalculationTooWideError, self.sut.worldPopulationRankByDate, 'unisex', 'WORLD', datetime(1930, 1, 1), datetime(2031, 1, 1))

    def test_byDate_unicodeRegions(self):
        # I don't care about the results, but at least one of these just shouldn't crash

        # test with the original latin1-encoded byte string
        latin1EncodedByteString = 'R\xe9union'
        self.assertTrue(self.sut.worldPopulationRankByDate('unisex', latin1EncodedByteString, datetime(1993, 12,  6), datetime.utcnow()) > 0)   # TODO: currently fails because latin1-encoded region names can not be looked up

        # test with a unicode string
        unicodeString = latin1EncodedByteString.decode('latin1')
        self.assertTrue(self.sut.worldPopulationRankByDate('unisex', unicodeString, datetime(1993, 12,  6), datetime.utcnow()) > 0)

        # test with an UTF8-encoded byte string
        utf8EncodedByteString = unicodeString.encode('utf-8')
        self.assertTrue(self.sut.worldPopulationRankByDate('unisex', utf8EncodedByteString, datetime(1993, 12,  6), datetime.utcnow()) > 0)
