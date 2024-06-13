import logging
import time

from rich.console import Console
from rich.logging import RichHandler

from .singleton import SingletonMeta


class AppLogger(metaclass=SingletonMeta):
    _logger = None

    def __init__(self):
        self._logger = logging.getLogger(__name__)

    def get_logger(self):
        return self._logger


class RichConsoleHandler(RichHandler):
    def __init__(self, width=300, style=None, **kwargs):
        super().__init__(
            console=Console(color_system="256", width=width, style=style), **kwargs
        )


class ElapsedTimeLogger:
    """
    Context manager to log elapsed time for code execution.

    Examples:
        Use `ElapsedTimeLogger` to measure and log the time taken by a block of code.

        ```python
        with ElapsedTimeLogger("Example task"):
            # Code block to measure time for
            time.sleep(2)
        ```

    Attributes:
        message (str): The message to log at the start and end of the context.
    """

    _logger = AppLogger().get_logger()

    def __init__(self, message):
        self.message = message

    def __enter__(self):
        self._logger.info(self.message)
        self.start = time.time()

    def __exit__(self, *args):
        elapsed_time = time.time() - self.start
        self._logger.info(f"Finished {self.message} in {elapsed_time} seconds")
