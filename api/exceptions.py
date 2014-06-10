from rest_framework.exceptions import ParseError



class InvalidSexError(ParseError):
    def __init__(self, invalidValue):
        self.detail = '%s is an invalid value for the parameter "sex", valid values are: male, female, unisex' % invalidValue

class InvalidCountryError(ParseError):
    def __init__(self, invalidValue):
        self.detail = '%s is an invalid value for the parameter "country", the list of valid values can be retrieved from the endpoint /meta/countries' % invalidValue

class DateParsingError(ParseError):
    def __init__(self, paramName, invalidValue):
        self.detail = 'The given date %s in parameter %s could not be parsed. Please provide dates in the format YYYY-MM-DD' % (invalidValue, paramName)

class NumberParsingError(ParseError):
    def __init__(self, paramName, invalidValue):
        self.detail = 'The given number %s in parameter %s could not be parsed. Please use digits only' % (invalidValue, paramName)

class OffsetParsingError(ParseError):
    def __init__(self, paramName, invalidValue):
        self.detail = 'The given offset %s in parameter %s could not be parsed. Valid values are a number to express days, or a combination of years, months and days in the format ##y##m##d' % (invalidValue, paramName)

class BirthdateOutOfRangeError(ParseError):
    def __init__(self, invalidValue):
        self.detail = 'The birthdate %s can not be processed, only dates between 1920-01-01 and today are supported' % invalidValue

class CalculationDateOutOfRangeError(ParseError):
    def __init__(self, invalidValue):
        self.detail = 'The calculation date %s can not be processed, only dates past 1950-01-01 and past the birthdate are supported' % invalidValue

class CalculationTooWideError(ParseError):
    def __init__(self, invalidValue):
        self.detail = 'The calculation date %s can not be processed, because only calculations up to an age of 100 years are supported' % invalidValue
