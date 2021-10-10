import select
from enum import Enum, unique

from flask import current_app
from siriuscommon import get_logger
from siriuscommon.devices.spreadsheet import SheetName

from ..exceptions import APIException
from ..status import HttpStatusCode

logger = get_logger("Spreadsheet Common")


@unique
class Command(Enum):
    GET_DEVICE = 1
    RELOAD_DATA = 2
    SHUTDOWN = 3


class InvalidCommand(APIException):
    status_code = HttpStatusCode.HTTP_400_BAD_REQUEST


class InvalidDevice(APIException):
    status_code = HttpStatusCode.HTTP_400_BAD_REQUEST

    def __init__(self, message: str):
        msg_detail = 'Available "deviceType" options are "{}".'.format(SheetName.keys())
        self.message = f"{message}\n{msg_detail}"


class BasicComm:
    def __init__(self):
        self.socket_timeout = 0

    def sendBytes(self, s, payload):
        LEN = len(payload)
        _num = 0
        while _num != LEN:
            ready = select.select([], [s], [], self.socket_timeout)
            if ready[1]:
                _num += s.send(payload[_num:])

    def recvBytes(self, s, LEN):
        _bytes = b""
        _num = 0
        while _num != LEN:
            ready = select.select([s], [], [], self.socket_timeout)
            if ready[0]:
                _bytes += s.recv(LEN - _num)
                _num = len(_bytes)
        return _bytes


SPREADSHEET_SOCKET_PATH = current_app.config.get("SPREADSHEET_SOCKET_PATH")
SPREADSHEET_XLSX_PATH = current_app.config.get("SPREADSHEET_XLSX_PATH")

logger.info('Using spreadsheet path at "{}".'.format(SPREADSHEET_XLSX_PATH))
logger.info('Using internal socket at "{}".'.format(SPREADSHEET_SOCKET_PATH))
