from games_nebula.client.translator import _tr

def convert_from_bytes(input_value, unit=None):
    """
    Convert size in bytes (int) to tuple of strings (size, unit) were size is size
    in bytes, kilobytes, megabyts or gygabytes (size converted to larger possible unit).
    Arguments:
        unit: force convertion to this unit
    """
    if not unit:
        if input_value/1024 < 1:
            return input_value, _tr("B")
        if input_value/1024**2 < 1:
            return f'{input_value/1024:.2f}', _tr("KB")
        if input_value/1024**3 < 1:
            return f'{input_value/1024**2:.2f}', _tr("MB")
        if input_value/1024**4 < 1:
            return f'{input_value/1024**3:.2f}', _tr("GB")
        else:
            return f'{input_value/1024**4:.2f}', _tr("TB")
    else:
        if unit == _tr('B'):
            return input_value, _tr("B")
        elif unit == _tr('KB'):
            return f'{input_value/1024:.2f}', _tr("KB")
        elif unit == _tr('MB'):
            return f'{input_value/1024**2:.2f}', _tr("MB")
        elif unit == _tr('GB'):
            return f'{input_value/1024**3:.2f}', _tr("GB")
        elif unit == _tr('TB'):
            return f'{input_value/1024**4:.2f}', _tr("TB")
        else:
            return input_value, _tr("B")
