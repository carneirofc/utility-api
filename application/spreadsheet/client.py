import os
import socket
import threading
import time
import typing

from siriuscommon.devices.spreadsheet import SheetName

from ..common.utils import get_logger
from .common import (
    BasicComm,
    Command,
    InvalidCommand,
    InvalidDevice,
    get_app_spreadsheet_socket_path,
    get_spreadsheet_xlsx_path,
)

CLIENT_SOCKET_TIMEOUT = 10


class SyncService:
    def __init__(self, spreadsheet_xlsx_path: str = None):
        self.spreadsheet_xlsx_path = (
            get_spreadsheet_xlsx_path()
            if not spreadsheet_xlsx_path
            else spreadsheet_xlsx_path
        )
        self.logger = get_logger("SyncService")
        self.thread = threading.Thread(target=self._doWork, daemon=True)
        self.update_time: typing.Optional[float] = None

    def start(self):
        self.logger.info("Starting sync service.")
        self.thread.start()

    def _tick(self):
        time.sleep(5)

    def _doWork(self):
        while True:
            self._tick()

            if not os.path.exists(self.spreadsheet_xlsx_path):
                continue

            current_update_time = os.path.getmtime(self.spreadsheet_xlsx_path)
            if not self.update_time or self.update_time != current_update_time:
                self._reload_spreadsheet_data(current_update_time)

    def _reload_spreadsheet_data(self, current_update_time):
        try:
            client = BackendClient()
            res = client.reloadData()
            if not res:
                raise Exception('Method "reloadData" returned False.')
            self.update_time = current_update_time
            self.logger.info(
                f'Update spreadsheet "{self.spreadsheet_xlsx_path}" at "{self.update_time}"'
            )
        except Exception:
            self.logger.exception("Failed to update the spreadsheet.")


class BackendClient(BasicComm):
    def __init__(self, socket_path: str = None):
        super().__init__()
        self.socket_path = (
            get_app_spreadsheet_socket_path() if not socket_path else socket_path
        )
        self.socket_timeout = CLIENT_SOCKET_TIMEOUT

        self.logger = get_logger("Client")
        self.logger.debug("BackendClient created")

    def sendCommand(self, payload: dict):
        if "command" not in payload:
            raise InvalidCommand('Missing "command"')

        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
            s.connect(self.socket_path)
            self._send_message(s, payload)
            response = self._recv_message(s)
            return response

    def reloadData(self):
        return self.sendCommand({"command": Command.RELOAD_DATA.value})

    def getDevice(self, ip: str, deviceType: str):
        if not deviceType or not (SheetName.has_sheet(deviceType)):
            raise InvalidDevice(f'Invalid device "{deviceType}".')

        return self.sendCommand(
            {
                "command": Command.GET_DEVICE.value,
                "ip": ip,
                "sheetName": SheetName.from_key(deviceType).value,
            }
        )
