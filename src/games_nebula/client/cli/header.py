from games_nebula import __version__
from games_nebula.client import config
from games_nebula.client.api_wrapper import Api
from games_nebula.client.translator import _tr
from games_nebula.client.cli import ansi
from games_nebula.client.cli.fancyprint import full_line_of
from games_nebula.client.cli.help import Help

def show():
    """Show application header with basic info."""
    api = Api(config.CONFIG_DIR)
    try:
        username = api.get_user_name()
    except:
        username = None
    ansi_text = ansi.AnsiText(disable=config.get('disable_colors'))
    translate_commands = Help()._is_trnaslation_required()
    translated_only = config.get('translated_commands_only')
    cmdstr_help = "help"
    if translate_commands:
        cmdstr_help = f'{cmdstr_help}/' + _tr("help")
        if translated_only:
            cmdstr_help = _tr("help")
    header = ansi_text.bold + ansi_text.fcolor_blue + \
            full_line_of('*') + '\n' + \
            ' ' + _tr("Games Nebula version") + f': {__version__} \n'
    if username:
        header += ' ' + _tr("Authorized user") + f': {username}\n'
    header += ' ' + _tr("For available commands type") + f' <{cmdstr_help}> ' + \
            _tr("or press TAB") + '.\n' + full_line_of('*') + ansi_text.reset_all
    print(header)
