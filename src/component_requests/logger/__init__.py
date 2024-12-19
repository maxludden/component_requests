from component_requests.logger.__main__ import get_console, get_logger, get_progress, on_exit
from component_requests.logger.sink import increment, read, rich_sink, setup, write
from rich.console import Console
from rich.traceback import install as tr_install

console = Console()
tr_install(console=console)

__all__ = [
    "rich_sink",
    "setup",
    "read",
    "write",
    "increment",
    "on_exit",
    "get_console",
    "get_logger",
    "get_progress",
]

setup()
