import signal
#
from utils.logger import log


# 只有在 gunicorn 下, 信号注册才生效.
class SigTerm:
    is_term = False
    term_handlers = []

    @classmethod
    def term_handler(cls, sig, frame):
        log.i('receive signal: sigTerm')
        assert sig == signal.SIGTERM
        #
        cls.is_term = True
        for handler in cls.term_handlers:
            handler()

    @classmethod
    def register(cls):
        """ 注册信号 """
        signal.signal(signal.SIGTERM, cls.term_handler)
        # signal.signal(signal.SIGINT, cls.default_signal_handler)
        # signal.signal(signal.SIGUSR1, cls.default_signal_handler)

    @classmethod
    def add_term_handler(cls, handler):
        cls.term_handlers.append(handler)
