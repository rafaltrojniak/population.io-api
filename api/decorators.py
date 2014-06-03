import functools
from api.exceptions import DateParsingError
from api.utils import str_to_datetime



def expect_datetime(param_name):
    def decorator(view_func):
        @functools.wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if param_name not in kwargs:
                raise RuntimeError('Parameter param_name to decorator @expect_datetime has to match one of the kwargs of the decorated function')

            # try to convert date_string into datetime, raise exception if this fails
            value = kwargs[param_name]
            try:
                new_value = str_to_datetime(param_name, value)
            except ValueError:
                raise DateParsingError(param_name, value)

            # inject converted datetime into the original function
            kwargs.update({param_name: new_value})

            # run the original view
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
