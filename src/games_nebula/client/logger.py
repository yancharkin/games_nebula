import os
import sys
import logging
import time

from games_nebula.client.cli import ansi
from games_nebula.client.translator import _tr

class Logger:
    """This class makes logging setup easier. Also adds colors to console output."""

    def __init__(self, log_dir=None, log_name=None, stream_fmt=None, file_fmt=None):
        self.__log_dir = log_dir
        self.__stream_fmt = stream_fmt
        self.__file_fmt = file_fmt
        self.__log_name = log_name
        self.__log_path = f'{log_dir}/{log_name}'

    def setup(self):
        """Setup logger. Make it output both into a file and stdout."""
        str_line = _tr("line")
        formatter = logging.Formatter((
                f'[%(levelname)s] %(message)s [%(asctime)s] '
                f'[%(filename)s, {str_line} %(lineno)s]'
        ))
        if not self.__stream_fmt:
            stream_formatter = formatter
        else:
            stream_formatter = logging.Formatter(self.__stream_fmt)
        stdout_handler = self.__StreamHandler(sys.stdout)
        stdout_handler.setFormatter(stream_formatter)
        handlers = [stdout_handler]
        if self.__log_name:
            if not os.path.exists(self.__log_dir):
                os.makedirs(self.__log_dir)
            if not self.__file_fmt:
                file_formatter = formatter
            else:
                file_formatter = logging.Formatter(self.__file_fmt)
            file_handler = logging.FileHandler(filename=self.__log_path, mode='w')
            file_handler.setFormatter(file_formatter)
            handlers.append(file_handler)
        logging.basicConfig(
                level = logging.DEBUG,
                handlers = handlers
        )

    class __StreamHandler(logging.StreamHandler):
        ansi_text = ansi.AnsiText()
        _levelNameToColor = {
                'CRITICAL': f'{ansi_text.bold}{ansi_text.fcolor_red}',
                'ERROR': f'{ansi_text.fcolor_red}',
                'WARNING': f'{ansi_text.fcolor_yellow}',
                'INFO': f'{ansi_text.bold}{ansi_text.fcolor_blue}',
                'DEBUG': f'{ansi_text.bold}{ansi_text.fcolor_magenta}'
        }
        def format(self, record):
            """Extend method by adding escape codes to output to make it colorful."""
            levelname = record.levelname
            formated_string = logging.StreamHandler.format(self, record)
            return f'{self._levelNameToColor[levelname]}{formated_string}{self.ansi_text.reset_all}'
