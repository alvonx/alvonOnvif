import logging
import os.path
from logging.handlers import TimedRotatingFileHandler


class ExtrasHelper:
    def __init__(self, isPrinting=True, divider='*', divider_count=25, color='blue', bold=True):
        self.isPrinting = isPrinting
        self.stars = divider * divider_count
        self.pcolor = color
        self.bold = bold

    def print_color(self, *input_content, ret=True):
        """i.e.  colorstr('blue', 'hello world')"""
        *args, string = input_content if len(input_content) > 1 else (self.pcolor, 'bold', input_content[0])  # color arguments, string
        if self.bold:
            args.append('bold') if 'bold' not in args else ''
        colors = {
            'black': '\033[30m',  # basic colors
            'red': '\033[31m',
            'green': '\033[32m',
            'yellow': '\033[33m',
            'blue': '\033[34m',
            'magenta': '\033[35m',
            'cyan': '\033[36m',
            'white': '\033[37m',
            'bright_black': '\033[90m',  # bright colors
            'bright_red': '\033[91m',
            'bright_green': '\033[92m',
            'bright_yellow': '\033[93m',
            'bright_blue': '\033[94m',
            'bright_magenta': '\033[95m',
            'bright_cyan': '\033[96m',
            'bright_white': '\033[97m',
            'end': '\033[0m',  # misc
            'bold': '\033[1m',
            'underline': '\033[4m'}
        if ret:
            return ''.join(colors[x] for x in args) + f'{string}' + colors['end']
        else:
            print(''.join(colors[x] for x in args) + f'{string}' + colors['end'])

    def exception_log_function(self, sys_info, error_msg, color='red'):
        exception_type, exception_object, exception_traceback = sys_info
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        print("Exception type: ", self.print_color(color, exception_type))
        print("File name: ", self.print_color(color, filename))
        print("Line number: ", self.print_color(color, line_number))
        print("Error message: ", self.print_color(color, error_msg))


class CreateLogger:
    def __init__(self, logger_name, log_file="app.log"):
        self.logger = None
        self.logger_name = logger_name
        self.log_file_path = None
        self.log_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), f'logs/{log_file}')
        if os.path.exists(self.log_file_path):
            pass
        else:
            # Creates a log file
            with open(self.log_file_path, 'w') as fp:
                fp.close()

    def __get_file_handler(self):
        file_handler = TimedRotatingFileHandler(self.log_file_path, when='midnight')
        FORMATTER = logging.Formatter("%(asctime)s -> %(name)s -> %(levelname)s -> %(pathname)s -> %(filename)s -> %(lineno)d -> %(message)s")
        file_handler.setFormatter(FORMATTER)
        return file_handler

    def get_logger(self):
        self.logger = logging.getLogger(self.logger_name)
        self.logger.setLevel(logging.DEBUG)  # better to have too much log than not enough
        if self.logger.hasHandlers():
            self.logger.handlers.clear()
        self.logger.addHandler(self.__get_file_handler())
        self.logger.propagate = False
        return self.logger


class AlertLogger:
    def __init__(self, logger_name, log_file="alert.txt"):
        self.logger = None
        self.logger_name = logger_name
        self.log_file_path = None
        self.log_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), f'alert_logs/{log_file}')
        if os.path.exists(self.log_file_path):
            pass
        else:
            # Creates a log file
            with open(self.log_file_path, 'w') as fp:
                fp.close()

    def __get_file_handler(self):
        file_handler = TimedRotatingFileHandler(self.log_file_path, when='midnight')
        FORMATTER = logging.Formatter("%(message)s")
        file_handler.setFormatter(FORMATTER)
        return file_handler

    def get_logger(self):
        self.logger = logging.getLogger(self.logger_name)
        self.logger.setLevel(logging.DEBUG)  # better to have too much log than not enough
        if self.logger.hasHandlers():
            self.logger.handlers.clear()
        self.logger.addHandler(self.__get_file_handler())
        self.logger.propagate = False
        return self.logger
