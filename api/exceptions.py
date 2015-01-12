from rest_framework.exceptions import ParseError
from api.utils import offset_to_str



class InvalidSexError(ParseError):
    def __init__(self, invalidValue):
        self.detail = '%s is an invalid value for the parameter "sex", valid values are: male, female, unisex' % invalidValue

class InvalidCountryError(ParseError):
    def __init__(self, invalidValue):
        self.detail = '%s is an invalid value for the parameter "country", the list of valid values can be retrieved from the endpoint /countries' % invalidValue

class InvalidContinentError(ParseError):
    def __init__(self, invalidValue):
        self.detail = '%s is an invalid value for the parameter "continent", the list of valid values can be retrieved from the endpoint /continent_countries' % invalidValue

class DateParsingError(ParseError):
    def __init__(self, paramName, invalidValue):
        self.detail = 'The given date %s in parameter %s could not be parsed. Please provide dates in the format YYYY-MM-DD' % (invalidValue, paramName)

class IntParsingError(ParseError):
    def __init__(self, paramName, invalidValue):
        self.detail = 'The given number %s in parameter %s could not be parsed. Please use digits only' % (invalidValue, paramName)

class FloatParsingError(ParseError):
    def __init__(self, paramName, invalidValue):
        self.detail = 'The given floating point number %s in parameter %s could not be parsed. Please use digits and the period only' % (invalidValue, paramName)

class OffsetParsingError(ParseError):
    def __init__(self, paramName, invalidValue):
        self.detail = 'The given offset %s in parameter %s could not be parsed. Valid values are a number to express days, or a combination of years, months and days in the format ##y##m##d' % (invalidValue, paramName)

class BirthdateOutOfRangeError(ParseError):
    def __init__(self, invalidValue, dateIntervalText):
        self.detail = 'The birthdate %s can not be processed, only dates %s are supported' % (invalidValue, dateIntervalText)

class EffectiveBirthdateOutOfRangeError(ParseError):
    def __init__(self, invalidValue):
        self.detail = 'The person\'s effective birthdate of %s is invalid, only birthdates past 2015-06-30 are supported' % invalidValue

class CalculationDateOutOfRangeError(ParseError):
    def __init__(self, invalidValue, dateIntervalText):
        self.detail = 'The calculation date %s can not be processed, only dates %s are supported' % (invalidValue, dateIntervalText)

class CalculationTooWideError(ParseError):
    def __init__(self, invalidValue):
        self.detail = 'The calculation date %s can not be processed, because only calculations up to an age of 100 years are supported' % invalidValue

class AgeOutOfRangeError(ParseError):
    def __init__(self, invalidValue):
        self.detail = 'The age %s can not be processed, because only calculations up to an age of 100 years are supported' % offset_to_str(invalidValue)

class DataOutOfRangeError(ParseError):
    def __init__(self, detail=None):
        self.detail = detail or 'The input data is out of range'
