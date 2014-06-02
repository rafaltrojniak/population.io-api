from django.test import SimpleTestCase
from datetime import datetime, timedelta

from api.algorithms import WorldPopulationRankCalculator



class TestWorldPopulationRankCalculation(SimpleTestCase):
    """
    Tests the world population rank calculation functions. All the reference values have been generated with the
    original R script (see modeling/R/).
    """

    DELTA = 100000

    @classmethod
    def setUpClass(cls):
        cls.sut = WorldPopulationRankCalculator()
        cls.sut.generateExtrapolationTable('PopTotal', 'WORLD')

    def test_byDate_today(self):
        self.assertAlmostEqual(56968930,   self.sut.worldPopulationRankByDate('PopTotal', 'WORLD', datetime(2013, 12, 31), datetime.utcnow()), delta=TestWorldPopulationRankCalculation.DELTA)
        self.assertAlmostEqual(2541533000, self.sut.worldPopulationRankByDate('PopTotal', 'WORLD', datetime(1993, 12,  6), datetime.utcnow()), delta=TestWorldPopulationRankCalculation.DELTA)
        self.assertAlmostEqual(4178598000, self.sut.worldPopulationRankByDate('PopTotal', 'WORLD', datetime(1980,  1,  1), datetime.utcnow()), delta=TestWorldPopulationRankCalculation.DELTA)
        self.assertAlmostEqual(5989566000, self.sut.worldPopulationRankByDate('PopTotal', 'WORLD', datetime(1960,  2, 29), datetime.utcnow()), delta=TestWorldPopulationRankCalculation.DELTA)
        self.assertAlmostEqual(7237177000, self.sut.worldPopulationRankByDate('PopTotal', 'WORLD', datetime(1915,  1,  1), datetime.utcnow()), delta=TestWorldPopulationRankCalculation.DELTA)

    def test_byDate_age(self):
        self.assertAlmostEqual(2541533000, self.sut.worldPopulationRankByDate('PopTotal', 'WORLD', datetime(1993, 12,  6), datetime(1993, 12,  6) + timedelta(days=7483)), delta=TestWorldPopulationRankCalculation.DELTA)
        self.assertAlmostEqual(1209918000, self.sut.worldPopulationRankByDate('PopTotal', 'WORLD', datetime(1993, 12,  6), datetime(1993, 12,  6) + timedelta(days=3650)), delta=TestWorldPopulationRankCalculation.DELTA)
        self.assertAlmostEqual(578344100,  self.sut.worldPopulationRankByDate('PopTotal', 'WORLD', datetime(1940,  5,  3), datetime(1940,  5,  3) + timedelta(days=3530)), delta=10*TestWorldPopulationRankCalculation.DELTA)
        self.assertAlmostEqual(217482,     self.sut.worldPopulationRankByDate('PopTotal', 'WORLD', datetime(1950,  1,  1), datetime(1950,  1,  1) + timedelta(days=0)),    delta=TestWorldPopulationRankCalculation.DELTA)

    def test_byDate_date(self):
        self.assertAlmostEqual(940947000,  self.sut.worldPopulationRankByDate('PopTotal', 'WORLD', datetime(1993, 12,  6), datetime(2001,  9, 11)), delta=TestWorldPopulationRankCalculation.DELTA)
        self.assertAlmostEqual(7203127000, self.sut.worldPopulationRankByDate('PopTotal', 'WORLD', datetime(1915,  1,  1), datetime(2014,  1,  1)), delta=TestWorldPopulationRankCalculation.DELTA)
