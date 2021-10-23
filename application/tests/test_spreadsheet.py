import os
import time
import unittest

from siriuscommon.devices.data_model import getBeaglesFromList, getDevicesFromBeagles
from siriuscommon.devices.spreadsheet import SheetName
from siriuscommon.devices.spreadsheet.parser import loadSheets

from application.spreadsheet.backend import BackendServer
from application.spreadsheet.client import BackendClient

SOCKET_PATH = os.path.abspath(
    os.path.join("application/tests/resources/redes_e_beaglebones.socket")
)

SPREADSHEET_PATH = os.path.abspath(
    os.path.join("application/tests/resources/Redes e Beaglebones.xlsx")
)


class TestParser(unittest.TestCase):
    def setUp(self):
        data = loadSheets(SPREADSHEET_PATH)
        self.data_agilent: dict = data[SheetName.AGILENT]
        self.data_mks: dict = data[SheetName.MKS]

    def test_data(self):
        self.assertGreater(self.data_agilent.__len__(), 0)
        self.assertGreater(self.data_mks.__len__(), 0)

    def checkTypes(self, data: dict):
        for device in getDevicesFromBeagles(getBeaglesFromList(data)):
            self.assertEqual(type(device.prefix), str)
            for channel in device.channels:
                self.assertEqual(type(channel.prefix), str)

    def test_agilent(self):
        self.checkTypes(self.data_agilent)

    def test_mks(self):
        self.checkTypes(self.data_mks)


class TestComm(unittest.TestCase):
    backend_server: BackendServer
    socket_path = SOCKET_PATH
    spreadsheet_path = SPREADSHEET_PATH

    def setUp(self):
        if not os.path.exists(self.spreadsheet_path):
            raise Exception(f"Missing spreadsheet {self.spreadsheet_path}")

        if os.path.exists(self.socket_path):
            os.remove(self.socket_path)

        self.backend_server = BackendServer(
            socket_path=self.socket_path, spreadsheet_xlsx_path=self.spreadsheet_path
        )
        self.backend_server.start()

        while not os.path.exists(self.socket_path):
            time.sleep(0.1)

    def tearDown(self) -> None:
        self.backend_server.stop()

    def test_commands(self):
        client = BackendClient(socket_path=self.socket_path)

        response = client.reloadData()
        self.assertTrue(response)

        for deviceType in SheetName.keys():
            response = client.getDevice(ip="", deviceType=deviceType)
            self.assertIsNotNone(response)
            self.assertIsInstance(response, dict)
