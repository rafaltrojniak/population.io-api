import functools
from api.exceptions import DateParsingError, OffsetParsingError, NumberParsingError
from api.utils import str_to_date, parse_offset



def expect_datetime(param_name):
    def decorator(view_func):
        @functools.wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if param_name not in kwargs:
                raise RuntimeError('View is decorated to process parameter %s, but this parameter is not declared as a keyword argument in the URL pattern' % param_name)

            # try to convert, raise exception if this fails
            value = kwargs[param_name]
            try:
                new_value = str_to_date(param_name, value)
            except ValueError:
                raise DateParsingError(param_name, value)

            # inject converted value into the original function
            kwargs.update({param_name: new_value})

            # run the original view
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def expect_number(param_name, optional=False):
    def decorator(view_func):
        @functools.wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not optional or param_name in kwargs:
                if param_name not in kwargs:
                    raise RuntimeError('View is decorated to process parameter %s, but this parameter is not declared as a keyword argument in the URL pattern' % param_name)

                # try to convert, raise exception if this fails
                if param_name in kwargs:
                    value = kwargs[param_name]
                    try:
                        new_value = int(value)
                    except ValueError:
                        raise NumberParsingError(param_name, value)
                elif optional:
                    new_value = None
                else:
                    raise RuntimeError('Missing parameter: ' + param_name)

                # inject converted value into the original function
                kwargs.update({param_name: new_value})

            # run the original view
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def expect_offset(param_name):
    def decorator(view_func):
        @functools.wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if param_name not in kwargs:
                raise RuntimeError('View is decorated to process parameter %s, but this parameter is not declared as a keyword argument in the URL pattern' % param_name)

            # try to convert, raise exception if this fails
            value = kwargs[param_name]
            new_value = parse_offset(value)
            if not new_value:
                raise OffsetParsingError(param_name, value)

            # inject converted value into the original function
            kwargs.update({param_name: new_value})

            # run the original view
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
