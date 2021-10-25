import multiprocessing
import os
import socket
from typing import Dict

from siriuscommon.devices.spreadsheet import SheetName
from siriuscommon.devices.spreadsheet.parser import loadSheets

from ..common.utils import get_logger
from .common import (
    BasicComm,
    Command,
    get_app_spreadsheet_socket_path,
    get_spreadsheet_xlsx_path,
)

SERVER_SOCKET_TIMEOUT = 5


class InvalidParameter(Exception):
    pass


class BackendServer(BasicComm):
    def __init__(self, socket_path: str = None, spreadsheet_xlsx_path: str = None):
        super().__init__()
        self.logger = get_logger("Backend")
        self.run = True
        self.spreadsheet_xlsx_path = (
            get_spreadsheet_xlsx_path()
            if not spreadsheet_xlsx_path
            else spreadsheet_xlsx_path
        )
        self.socket_path = (
            get_app_spreadsheet_socket_path() if not socket_path else socket_path
        )
        self.socket_timeout = SERVER_SOCKET_TIMEOUT
        self.process = multiprocessing.Process(target=self.listen, daemon=True)

        self.sheetsData: Dict[SheetName, dict] = {}

    def stop(self):
        self.logger.info("Shutting down backend server process.")
        self.process.kill()

    def start(self):
        self.logger.info("Starting backend server process.")
        self.process.start()

    def listen(self):
        if os.path.exists(self.socket_path):
            os.remove(self.socket_path)
            self.logger.warning(f'Removing socket at "{self.socket_path}"')

        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
            s.bind(self.socket_path)
            s.listen()
            self._socket_listen(s)

        self.logger.info("Shutting down gracefully.")

    def _socket_listen(self, s: socket.socket):
        while self.run:
            self.logger.debug(f'Waiting for a connection at "{self.socket_path}" ...')
            conn, _addr = s.accept()
            self.logger.debug("Client connected ...")
            self._handle_client(conn)
        self.logger.info("Socket shutting down")

    def _handle_client(self, conn: socket.socket):
        with conn:
            try:
                conn.setblocking(False)
                payload = self._recv_message(conn)
                response = self.handle(payload)
                self._send_message(conn, response)

            except InvalidParameter as e:
                msg = f'Invalid paylad content. "{e}"'
                self.logger.error(msg)
                self._send_message(conn, {"status": "failure", "error": msg})

            except Exception:
                self.logger.exception(
                    f"Unexpected exception, the connection with the unix socket {self.socket_path} has been closed."
                )
            self.logger.debug("Connection with client closed.")

    def handle(self, payload: dict):
        command = payload["command"]
        self.logger.info(f"Handle: {payload}")

        if command == Command.GET_DEVICE:
            return self.getDevice(sheetName=payload.get("sheetName", ""))
        elif command == Command.RELOAD_DATA:
            self.sheetsData = loadSheets(self.spreadsheet_xlsx_path)
            return True

        return {"status": "failure", "error": "invalid command"}

    def getDevice(self, sheetName: str, **kwargs):
        return self.sheetsData.get(sheetName, {})
