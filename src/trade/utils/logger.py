import logging


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
        #
        self._logger = logging.getLogger(name)  # if no name is specified, return root logger of the hierarchy
        self._logger.addHandler(hdlr=self.get_stream_handler())
        self.set_level(log_level='debug')
        self.set_header(log_header=header)

    @staticmethod
    def get_stream_handler():
        # 日志格式示例: 2019-08-04 07:52:25.210 [INFO] text
        date_fmt = "%Y-%m-%d %H:%M:%S"
        fmt = "%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s"     # 查看源码: logging/__init__.py: class Formatter
        formatter = logging.Formatter(fmt=fmt, datefmt=date_fmt)        # 查看源码: logging/__init__.py: def formatTime
        #
        handler = logging.StreamHandler(stream=None)
        handler.setFormatter(fmt=formatter)
        return handler

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
