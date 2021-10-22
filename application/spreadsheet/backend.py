import os
import pickle
import socket
import threading
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
        self.thread = threading.Thread(target=self.listen, daemon=True)

        self.sheetsData: Dict[SheetName, dict] = {}

    def start(self):
        self.logger.info("Starting backend server thread.")
        self.thread.start()

    def fromClient(self, conn):
        payload_bytes = b""
        payload_length = int.from_bytes(self.recvBytes(conn, 4), "big")
        payload_bytes = self.recvBytes(conn, payload_length)

        return payload_bytes

    def toClient(self, conn, response):
        response_length = len(response)

        self.sendBytes(conn, response_length.to_bytes(4, "big"))
        self.sendBytes(conn, response)

    def listen(self):
        if os.path.exists(self.socket_path):
            os.remove(self.socket_path)
            self.logger.warning('Removing socket at "{}"'.format(self.socket_path))

        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
            s.bind(self.socket_path)
            s.listen()
            self._socket_listen(s)

        self.logger.info("Shutting down gracefully.")

    def _socket_listen(self, s: socket.socket):
        while self.run:
            self.logger.debug(
                'Waiting for a connection at "{}" ...'.format(self.socket_path)
            )
            conn, _addr = s.accept()
            self.logger.debug("Client connected ...")
            self._handle_client(conn)

    def _handle_client(self, conn: socket.socket):
        with conn:
            try:
                conn.setblocking(False)
                payload_bytes = self.fromClient(conn)
                if payload_bytes != b"":
                    payload = pickle.loads(payload_bytes)
                    response = pickle.dumps(self.handle(payload))
                    self.toClient(conn, response)

            except InvalidParameter as e:
                self.logger.error('Invalid paylad content. "{}"'.format(e))
                self.toClient(conn, pickle.dumps({}))

            except Exception:
                self.logger.exception(
                    "The connection with the unix socket {} has been closed."
                )
            self.logger.debug("Connection with client closed.")

    def handle(self, payload: dict):
        command = payload["command"]
        self.logger.info("Handle: {}".format(payload))

        if command == Command.GET_DEVICE:
            return self.getDevice(**payload)
        elif command == Command.RELOAD_DATA:
            self.sheetsData = loadSheets(self.spreadsheet_xlsx_path)
            return True

        return None

    def getDevice(self, sheetName: SheetName = None, **kwargs):
        return self.sheetsData.get(sheetName, {})
