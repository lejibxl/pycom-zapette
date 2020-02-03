
from logging.logging import LoggingHandler
from zapette.zapette import send_frame_TX

class ZapetteHandler(LoggingHandler):

    def __init__(self, zapette):
        """Create an instance.

        :param zapette: the lora trap  to which to write messages

        """
        self._zapette = zapette

    def format(self, level, msg):
        """Generate a string to log.

        :param level: The level at which to log
        :param msg: The core message

        """
        return super().format(level, msg) + '\r\n'

    def emit(self, level, msg):
        """Generate the message and write it to the UART.

        :param level: The level at which to log
        :param msg: The core message

        """
        send_frame_TX(self.format(level,msg))
