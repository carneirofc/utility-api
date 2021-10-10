#!/usr/bin/env python3

import unittest

from siriuscommon.devices.data_model import getBeaglesFromList, getDevicesFromBeagles
from siriuscommon.devices.spreadsheet import SheetName
from siriuscommon.devices.spreadsheet.parser import loadSheets


class TestParser(unittest.TestCase):
    def setUp(self):
        data = loadSheets("Redes e Beaglebones.xlsx")
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


if __name__ == "__main__":
    unittest.main()
