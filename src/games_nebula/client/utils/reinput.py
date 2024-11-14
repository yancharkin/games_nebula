from games_nebula.client.cli.ansi import AnsiCommands
from games_nebula.client.translator import _tr

def reinput(prompt, length=0, numeric=False):
    """Improved input function."""
    user_input = ''
    condition_length = bool(length)
    condition_numeric = numeric
    while not user_input or condition_length or condition_numeric:
        try:
            user_input = input(f'\r\033[2K{prompt}')
        except KeyboardInterrupt:
            pass
        except EOFError:
            user_input = ''
            break
        if length:
            condition_length = len(user_input) < length
            if condition_length:
                print(_tr("The minimum number of characters is") + f': {length}.')
        if numeric:
            condition_numeric = not user_input.isnumeric()
            if length:
                condition_numeric = not user_input[:length].isnumeric()
            if condition_numeric:
                print(_tr("Only numeric characters are allowed."))
    AnsiCommands().erase_prev_line()
    return user_input
