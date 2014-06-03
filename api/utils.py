import datetime



def str_to_datetime(param_name, date_string):
    return datetime.datetime.strptime(date_string, '%Y-%m-%d')

def datetime_to_str(datetime_obj):
    return datetime_obj.strftime('%Y-%m-%d')
