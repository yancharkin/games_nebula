import curses

from games_nebula.client.cli import ansi

curses.setupterm()

def fancyprint(text, foreground_color=None, background_color=None):
    """
    Print text in different colors.
    Simple example:
        fancyprint('hello world', 'black', 'white')
    Complex example (first world red and second green):
        fancyprint('hello world', {'red': [0], 'green': [1]}, 'black')
    """
    if foreground_color:
        fcolor = ansi.AnsiText()
        if type(foreground_color) == str:
            try:
                color = getattr(fcolor, f'fcolor_{foreground_color}')
                text = f'{color}{text}'
            except:
                pass
        elif type(foreground_color) == dict:
            text_list = text.split()
            for color_name, indices in foreground_color.items():
                for i in indices:
                    try:
                        color = getattr(fcolor, f'fcolor_{color_name}')
                        text_list[i] = f'{color}{text_list[i]}'
                    except:
                        pass
            text = ' '.join(text_list)
    if background_color:
        bcolor = ansi.Text()
        if type(background_color) == str:
            try:
                color = getattr(bcolor, f'bcolor_{background_color}')
                text = f'{color}{text}'
            except:
                pass
        elif type(background_color) == dict:
            text_list = text.split()
            for color_name, indices in background_color.items():
                for i in indices:
                    try:
                        color = getattr(bcolor, f'bcolor_{color_name}')
                        text_list[i] = f'{color}{text_list[i]}'
                    except:
                        pass
            text = ' '.join(text_list)
    print(text)

def full_line_of(char):
    """Print a whole line of specified character."""
    return curses.tigetnum('cols') * char
