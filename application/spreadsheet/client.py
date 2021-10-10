import os
import pickle
import socket
import threading
import time

from siriuscommon import get_logger
from siriuscommon.devices.spreadsheet import SheetName

from .common import (
    SPREADSHEET_SOCKET_PATH,
    SPREADSHEET_XLSX_PATH,
    BasicComm,
    Command,
    InvalidCommand,
    InvalidDevice,
)

CLIENT_SOCKET_TIMEOUT = 10


class SyncService:
    def __init__(self):
        self.logger = get_logger("SyncService")
        self.thread = threading.Thread(target=self.doWork, daemon=True)
        self.update_time = None

    def start(self):
        self.logger.info("Starting sync service.")
        self.thread.start()

    def doWork(self):
        while True:
            if os.path.exists(SPREADSHEET_XLSX_PATH):
                current_update_time = os.path.getmtime(SPREADSHEET_XLSX_PATH)
                if not self.update_time or self.update_time != current_update_time:
                    try:
                        client = BackendClient()
                        res = client.reloadData()
                        if not res:
                            raise Exception('Method "reloadData" returned False.')
                        self.update_time = current_update_time
                        self.logger.info(
                            'Update spreadsheet from "{}" at time "{}"'.format(
                                SPREADSHEET_XLSX_PATH, self.update_time
                            )
                        )
                    except Exception:
                        self.logger.exception("Failed to update the spreadsheet.")
            time.sleep(5)


class BackendClient(BasicComm):
    def __init__(self):
        self.socket_path = SPREADSHEET_SOCKET_PATH
        self.socket_timeout = CLIENT_SOCKET_TIMEOUT

        self.logger = get_logger("Client")
        self.logger.debug("BackendClient created")

    def sendCommand(self, payload: dict):
        if "command" not in payload:
            raise InvalidCommand('Missing "command"')

        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
            s.connect(self.socket_path)
            payload_bytes = pickle.dumps(payload)
            payload_length = len(payload_bytes).to_bytes(4, "big")

            self.sendBytes(s, payload_length)
            self.sendBytes(s, payload_bytes)

            response_len = int.from_bytes(self.recvBytes(s, 4), "big")
            response_bytes = self.recvBytes(s, response_len)
            response = pickle.loads(response_bytes)
            return response

    def reloadData(self):
        return self.sendCommand({"command": Command.RELOAD_DATA})

    def getDevice(self, ip, deviceType):
        if not (deviceType in SheetName):
            raise InvalidDevice('Invalid device "{}".'.format(deviceType))

        return self.sendCommand(
            {
                "command": Command.GET_DEVICE,
                "ip": ip,
                "sheetName": SheetName.from_key(deviceType),
            }
        )
