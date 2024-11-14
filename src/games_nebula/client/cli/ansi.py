"""
ANSI Escape Sequences.
https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797
"""

class AnsiCommands:
    """Contains functions that perform certain actions by combining ANSI codes."""

    def __init__(self):
        pass
    def clear_screen(self):
        """Clear the terminal screen."""
        print('\033[2J\033[H', end='', flush=True)

    def erase_line(self):
        """Erase a line and reset a cursor's position."""
        print(f'\r\033[2K', end='', flush=True)

    def erase_prev_line(self):
        """Erase previous line."""
        print('\033[1A\033[K', end='', flush=True)

    def print_on_the_same_line(self, text):
        """Erase a line and print without moving to new line."""
        print(f'\r\033[2K{text}', end='', flush=True)

class AnsiText:
    """Aliases for ANSI color codes and graphics modes."""

    def __init__(self, disable=False):
        self.reset_all = '\033[0m'
        self.bold = '\033[1m'
        self.bold_reset = '\033[22m'
        self.faint = '\033[2m'
        self.faint_reset = '\033[22m'
        self.italic = '\033[3m'
        self.italic_reset = '\033[23m'
        self.underline = '\033[4m'
        self.underline_reset = '\033[24m'
        self.blinking = '\033[5m'
        self.blinking_reset = '\033[25m'
        self.inverse = '\033[7m'
        self.inverse_reset = '\033[27m'
        self.invisible = '\033[8m'
        self.invisible_reset = '\033[28m'
        self.strikethrough = '\033[9m'
        self.strikethrough_reset = '\033[29m'
        self.fcolor_black = '\033[30m'
        self.fcolor_red = '\033[31m'
        self.fcolor_green = '\033[32m'
        self.fcolor_yellow = '\033[33m'
        self.fcolor_blue = '\033[34m'
        self.fcolor_magenta = '\033[35m'
        self.fcolor_cyan = '\033[36m'
        self.fcolor_white = '\033[37m'
        self.bcolor_black = '\033[40m'
        self.bcolor_red = '\033[41m'
        self.bcolor_green = '\033[42m'
        self.bcolor_yellow = '\033[43m'
        self.bcolor_blue = '\033[44m'
        self.bcolor_magenta = '\033[45m'
        self.bcolor_cyan = '\033[46m'
        self.bcolor_white = '\033[47m'
        if disable:
            for attr in dir(self):
                if not attr.startswith('__'):
                    setattr(self, attr, '')

