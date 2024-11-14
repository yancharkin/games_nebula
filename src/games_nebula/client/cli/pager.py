"""Module contains simple pager and functions that prepare data for it."""
import curses

from games_nebula.client.translator import _tr
from games_nebula.client.cli import ansi
from games_nebula.client.cli.fancyprint import full_line_of

curses.setupterm()

def convert_to_list(data):
    """
    Convert data (usually string) to list.
    Prepare it for using with pager function.
    """
    if type(data) != list:
        line_length = curses.tigetnum('cols')
        data = str(data)
        data_list = []
        for subdata in data.split('LINEBREAK'):
            subdata_list = []
            i = 0
            if subdata.strip(): # check if there anything beside whitespaces
                while i < len(subdata):
                    subdata_list.append(subdata[i:i+line_length])
                    i += line_length
            data_list.extend(subdata_list)
            data = data_list
    return data

def pager(data):
    """Simple pager."""
    ansi_commands = ansi.AnsiCommands()
    n_lines = curses.tigetnum('lines') - 3
    data = convert_to_list(data)
    for i, item in enumerate(data):
        try:
            if i % n_lines == 0 and i != 0:
                print(full_line_of('-'))
                print(_tr("Press 'Enter' to show the next page."))
                input()
                ansi_commands.erase_prev_line()
                print(item)
            else:
                print(item)
        except (KeyboardInterrupt, EOFError):
            ansi_commands.erase_prev_line()
            break

def remove_html_tags(string):
    """
    Remove HTML tags from the text.
    Prepare the text for using with pager function.
    """
    # Preserve links but remove tags
    all_links = [x.split('>')[0].replace('"', '') for x in string.split('<a href=') if '"http' in x]
    splitted_string = string.split('</a>')
    for link in all_links:
        if splitted_string[0][-1] == '.':
            splitted_string[0] = splitted_string[0][:-1]
        splitted_string[0] = f': {link}'.join(splitted_string[0:2])
        if len(splitted_string) > 1:
            del(splitted_string[1])
    string = splitted_string[0]
    # Preserve lists
    string = string.replace('<ul>', 'LINEBREAK')
    string = string.replace('<ol>', 'LINEBREAK')
    string = string.replace('</li>', 'LINEBREAK')
    # Headers take up the whole line
    for i in range(1, 7):
        string = string.replace(f'<h{i}>', 'LINEBREAK')
        string = string.replace(f'</h{i}>', 'LINEBREAK')
    # Remove anything that looks like an html tag
    new_string = ''
    skip_char = False
    for char in string:
        if char == '<':
            skip_char = True
        elif char == '>':
            skip_char = False
        if (not skip_char) and (char != '>'):
            new_string += char
    string = new_string.strip(': ')
    string = ' '.join(string.split()) # remove extra whitespaces
    return string

#def strip_lead(string, chars=' '):
#    """Remove 'chars' from the beginning of the string"""
#    if string == '':
#        return string
#    for i in range(len(string)):
#        if string[i] not in chars:
#            return string[i:]
