import logging
import sys

def msg_debug(msg, cls=None):
    if cls is None:
        logging.debug('{}: {}'.format(sys._getframe(1).f_code.co_name,
                                      msg))
    else:
        logging.debug('{}.{}: {}'.format(cls.__name__,
                                         sys._getframe(1).f_code.co_name,
                                         msg))
