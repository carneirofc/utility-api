import json
import select
from enum import Enum, unique
from socket import socket

from flask import current_app
from siriuscommon.devices.spreadsheet import SheetName

from ..common.exceptions import APIException
from ..common.status import HttpStatusCode
from ..common.utils import get_logger

logger = get_logger("Spreadsheet Common")


@unique
class Command(int, Enum):
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
    _socket_timeout = 0
    _message_len_size = 4
    _message_byte_order = "big"
    _message_encoding = "utf-8"

    def _recv_message(self, s: socket) -> dict:
        response_len = int.from_bytes(
            self._recv_bytes(s, self._message_len_size), self._message_byte_order
        )
        response_bytes = self._recv_bytes(s, response_len)
        response_str = response_bytes.decode("utf-8")
        return json.loads(response_str)

    def _send_message(self, s: socket, payload: dict):
        payload_bytes = json.dumps(payload).encode(self._message_encoding)
        payload_length = len(payload_bytes).to_bytes(
            self._message_len_size, self._message_byte_order
        )

        self._send_bytes(s, payload_length)
        self._send_bytes(s, payload_bytes)

    def _send_bytes(self, s: socket, payload: bytes):
        LEN = len(payload)
        _num = 0
        while _num != LEN:
            __rlist, __wlist, __xlist = select.select([], [s], [], self._socket_timeout)
            if __wlist:
                _num += s.send(payload[_num:])

    def _recv_bytes(self, s: socket, LEN: int):
        _bytes = b""
        _num = 0
        while _num != LEN:
            __rlist, __wlist, __xlist = select.select([s], [], [], self._socket_timeout)
            if __rlist:
                _bytes += s.recv(LEN - _num)
                _num = len(_bytes)
        return _bytes


def get_app_spreadsheet_socket_path():
    return current_app.config.get("SPREADSHEET_SOCKET_PATH")


def get_spreadsheet_xlsx_path():
    return current_app.config.get("SPREADSHEET_XLSX_PATH")
