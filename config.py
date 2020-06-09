"""Flask config class."""
import os


class Config:
    """Base config vars."""

    DEBUG = False
    TESTING = False
    USE_RELOADER = False

    SECRET_KEY = os.environ.get("SECRET_KEY", "")
    REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")

    """ This can be an url or a filesystem path.
        If it's a filesystem path, it will automatically be updated when the file changes. """
    SPREADSHEET_XLSX_PATH = os.environ.get(
        "SPREADSHEET_XLSX_PATH",
        "http://10.0.38.42/streamdevice-ioc/Redes%20e%20Beaglebones.xlsx",
    )
    SPREADSHEET_SOCKET_PATH = os.environ.get(
        "SPREADSHEET_SOCKET_PATH", "/var/tmp/devices_socket"
    )
