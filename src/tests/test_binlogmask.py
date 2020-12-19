import os
import sys
import importlib

from unittest import TestCase

sys.path.append(os.path.join(os.path.dirname(__file__), '../bin'))

binlogmaskmoj = importlib.import_module("mita2-binlog-mask")

class TestBinlogMask(TestCase):

    def test_shift_date(self):
        binlogmask = binlogmaskmoj.BinlogMask()
        shifted = binlogmask.shift_date('2020-12-10 10:00:00', 14 * 60 + 39)
        self.assertEqual("2020-12-10 10:14:39", shifted)
