import os
import time
import logging


class MyFormatter(logging.Formatter):
    pass
    # def format(self, record):
    #     msg = logging.Formatter.format(self, record)
    #     if isinstance(msg, str):
    #         msg = msg.decode('utf8', 'replace')
    #     return msg


class Logger(object):
    _logger = None
    #
    CLOSE = 0                       # 0
    TRACE = 1                       # 1
    DEBUG = logging.DEBUG           # 10
    INFO = logging.INFO             # 20
    WARN = logging.WARN             # 30
    ERROR = logging.ERROR           # 40
    CRITICAL = logging.CRITICAL     # 50
    #

    def __init__(self, header='', name='default'):
        self._log_header = 'header'
        self._log_directory = './'
        # 日志格式示例: 2019-08-04 07:52:25.210 [INFO] text
        self.fmt = "%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s"     # 查看源码: logging/__init__.py: class Formatter
        self.date_fmt = "%Y-%m-%d %H:%M:%S"
        #
        self._logger = logging.getLogger(name)  # if no name is specified, return root logger of the hierarchy
        self._logger.addHandler(hdlr=self.get_stream_handler())
        self._logger.addHandler(hdlr=self.get_file_handler())
        self.set_level(log_level='debug')
        self.set_header(log_header=header)

    def get_stream_handler(self):
        handler = logging.StreamHandler(stream=None)
        handler.setFormatter(fmt=logging.Formatter(fmt=self.fmt, datefmt=self.date_fmt))
        return handler

    def get_file_handler(self):
        handler = logging.FileHandler(filename=self.get_filename(), mode='a', encoding='utf-8')
        handler.setFormatter(MyFormatter(fmt=self.fmt, datefmt=self.date_fmt))
        return handler

    def get_filename(self) -> str:
        """ {header}_{yyyymmdd}_{pid}.log """
        yyyymmdd = time.strftime("%Y%m%d", time.localtime())
        pid = os.getpid()
        return os.path.join(self._log_directory, f'{self._log_header}_{yyyymmdd}_{pid}.log')

    def set_level(self, log_level: str):
        """
        :param log_level: debug, info, warn, error
        :return:
        """
        self._logger.setLevel(self.get_level(log_level=log_level))

    def get_level(self, log_level: str):
        level = getattr(self, log_level.upper(), None)
        if not level:
            raise Exception(f'unknown log_level: {log_level}')
        return level

    def get_level_int(self) -> int:
        return self._logger.getEffectiveLevel()

    def set_header(self, log_header: str):
        self._log_header = log_header

    def set_directory(self, log_directory: str):
        self._log_directory = log_directory

    def set_buffer(self, log_buffer_size: int):
        # TODO 未完成
        pass

    def i(self, msg, *args, **kwargs):
        self._logger.info(msg, *args, **kwargs)

    def e(self, msg, *args, **kwargs):
        self._logger.error(msg, *args, **kwargs)

    def w(self, msg, *args, **kwargs):
        self._logger.warning(msg, *args, **kwargs)

    def d(self, msg, *args, **kwargs):
        self._logger.debug(msg, *args, **kwargs)

    def t(self, msg, *args, **kwargs):  # more debug info
        if self.get_level_int() == self.TRACE:
            self._logger.debug(msg, *args, **kwargs)

    def close(self):
        if self._logger:
            for handler in self._logger.handlers:
                handler.close()
                self._logger.removeHandler(handler)


log = Logger()
