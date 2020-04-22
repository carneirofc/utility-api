from enum import Enum, unique
from flask import current_app
from application.utils import get_logger

logger = get_logger("Spreadsheet Common")


@unique
class Command(Enum):
    GET_DEVICE = 1
    RELOAD_DATA = 2
    SHUTDOWN = 3


@unique
class Devices(Enum):
    AGILENT = "agilent"
    MKS = "mks"


DevicesList = set()
for device in Devices:
    DevicesList.add(device.value)

SPREADSHEET_SOCKET_PATH = current_app.config.get("SPREADSHEET_SOCKET_PATH")
SPREADSHEET_XLSX_PATH = current_app.config.get("SPREADSHEET_XLSX_PATH")

logger.info('Using spreadsheet path at "{}".'.format(SPREADSHEET_XLSX_PATH))
logger.info('Using internal socket at "{}".'.format(SPREADSHEET_SOCKET_PATH))
