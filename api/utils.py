import datetime, re, math
from dateutil.relativedelta import relativedelta



def str_to_date(param_name, date_string):
    return datetime.datetime.strptime(date_string, '%Y-%m-%d').date()

OFFSET_REGEX = re.compile(r'^(?:(?P<years>\d+)y)?(?:(?P<months>\d+)m)?(?:(?P<days>\d+)d)?$')
def parse_offset(val):
    if val.isdigit():
        return relativedelta(days=int(val))
    else:
        re_result = OFFSET_REGEX.match(val)
        if re_result and re_result.lastindex:   # lastindex is None (and has_any_match therefore False) if all three optional groups were left off
            years, months, days = (int(x) if x else 0 for x in re_result.groups())
            return relativedelta(years=years, months=months, days=days)
    return None

def offset_to_str(offset):
    return '' + ('%iy' % offset.years if offset.years else '') + ('%im' % offset.months if offset.months else '') + ('%id' % offset.days if offset.days else '')

def decimal_years_to_relativedelta(years_float):
    years = math.trunc(years_float)
    days = math.trunc((years_float% 1)*365)
    return relativedelta(years=years, days=days)

def relativedelta_to_decimal_years(offset):
    return offset.years * 1.0 + offset.months / 12.0 + offset.days / 365.0
