import functools
from datetime import datetime

from django.conf import settings
from django.utils.cache import patch_cache_control
from django.views.decorators.cache import cache_control
from api.exceptions import DateParsingError, OffsetParsingError, IntParsingError, FloatParsingError
from api.utils import str_to_date, parse_offset


def build_decorator(conversion_function):
    """ Helper function, that builds a standard parameter conversion decorator from a conversion function """
    def decorator_with_param_generator(param_name, optional=False):
        def decorator(view_func):
            @functools.wraps(view_func)
            def _wrapped_view(request, *args, **kwargs):
                # unless this parameter is optional, not specifying it is an error
                if not optional and param_name not in kwargs:
                    raise RuntimeError('View is decorated to process parameter %s, but this parameter is not declared as a keyword argument in the URL pattern' % param_name)
                # if it's optional and not given, that's fine
                elif optional and param_name not in kwargs:
                    pass
                # otherwise, we know the parameter is given
                else:
                    # run the conversion
                    value = kwargs[param_name]
                    new_value = conversion_function(param_name, value)

                    # inject converted value into the original function
                    kwargs.update({param_name: new_value})

                # run the original view
                return view_func(request, *args, **kwargs)
            return _wrapped_view
        return decorator
    return decorator_with_param_generator

def normalize_int(param_name, value):
    try:
        return int(value)
    except ValueError:
        raise IntParsingError(param_name, value)
expect_int = build_decorator(normalize_int)

def normalize_float(param_name, value):
    try:
        return float(value)
    except ValueError:
        raise FloatParsingError(param_name, value)
expect_float = build_decorator(normalize_float)

def normalize_date(param_name, value):
    try:
        return str_to_date(param_name, value)
    except ValueError:
        raise DateParsingError(param_name, value)
expect_date = build_decorator(normalize_date)

def normalize_offset(param_name, value):
    new_value = parse_offset(value)
    if not new_value:
        raise OffsetParsingError(param_name, value)
    return new_value
expect_offset = build_decorator(normalize_offset)

def cache_unlimited():
    """
    Decorates a view function to set a Cache-Control header with an expiration timeout of settings.CACHE_CONTROL_MAXAGE seconds.
    """
    return cache_control(public=True, max_age=settings.CACHE_CONTROL_MAXAGE)

def cache_until_utc_eod():
    """
    Decorates a view function to set a Cache-Control header with an expiration date of midnight UTC (or maximum settings.CACHE_CONTROL_MAXAGE,
    in case that value is set to less than a day).
    """

    def calculate_max_age():
        utc_eod = datetime.utcnow().replace(hour=23, minute=59, second=59, microsecond=0)
        time_until_utc_eod = utc_eod - datetime.utcnow()
        positive_seconds_until_utc_eod = max(0, int(time_until_utc_eod.total_seconds()))
        max_age = min(positive_seconds_until_utc_eod, settings.CACHE_CONTROL_MAXAGE)
        return max_age

    # modification of @django.views.decorators.cache.cache_control
    def _cache_controller(viewfunc):
        @functools.wraps(viewfunc)
        def _cache_controlled(request, *args, **kw):
            max_age = calculate_max_age()
            response = viewfunc(request, *args, **kw)
            patch_cache_control(response, public=True, max_age=max_age)
            return response
        return _cache_controlled
    return _cache_controller
