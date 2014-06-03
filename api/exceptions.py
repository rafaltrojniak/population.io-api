from rest_framework.exceptions import ParseError
from api.utils import datetime_to_str



class InvalidSexError(ParseError):
    def __init__(self, invalidValue):
        self.detail = '%s is an invalid value for the parameter "sex", valid values are: male, female, unisex' % invalidValue

class InvalidRegionError(ParseError):
    def __init__(self, invalidValue):
        self.detail = '%s is an invalid value for the parameter "region", the list of valid values can be retrieved from the endpoint /meta/countries' % invalidValue

class DateParsingError(ParseError):
    def __init__(self, paramName, invalidValue):
        self.detail = 'The given date %s in parameter %s could not be parsed. Please provide dates in the format YYYY-MM-DD' % (datetime_to_str(invalidValue), paramName)

class BirthdateOutOfRangeError(ParseError):
    def __init__(self, invalidValue):
        self.detail = 'The birthdate %s can not be processed, only dates between 1920-01-01 and today are supported' % datetime_to_str(invalidValue)

class CalculationDateOutOfRangeError(ParseError):
    def __init__(self, invalidValue):
        self.detail = 'The calculation date %s can not be processed, only dates past 1950-01-01 and past the birthdate are supported' % datetime_to_str(invalidValue)

class CalculationTooWideError(ParseError):
    def __init__(self, invalidValue):
        self.detail = 'The calculation date %s can not be processed, because only calculations up to an age of 100 years are supported' % datetime_to_str(invalidValue)
