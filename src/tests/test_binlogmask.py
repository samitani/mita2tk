import os
import sys
import random
import importlib

from unittest import TestCase

sys.path.append(os.path.join(os.path.dirname(__file__), '../bin'))

binlogmaskmoj = importlib.import_module("mita2-binlog-mask")

class TestBinlogMask(TestCase):

    def test_shift_datetime(self):
        binlogmask = binlogmaskmoj.BinlogMask()
        shifted = binlogmask.shift_datetime('2020-12-10 10:00:00', (24 * 60 * 60 * 2) + (14 * 60) + 39)
        self.assertEqual("2020-12-12 10:14:39", shifted)

    def test_shift_date(self):
        binlogmask = binlogmaskmoj.BinlogMask()
        shifted = binlogmask.shift_date('2020:12:10', (24 * 60 * 60 * 2) + (14 * 60) + 39)
        self.assertEqual("2020:12:12", shifted)

    def test_mask_integers(self):
        binlogmask = binlogmaskmoj.BinlogMask()

        str1 = "###   @1=0 /* TINYINT meta=0 nullable=1 is_null=0 */"
        self.assertRegex(binlogmask.mask_values(str1, 0), r'###   @1=[0-9]+ /\* TINYINT meta=0 nullable=1 is_null=0 \*/')

        str2 = "###   @2=0 /* SHORTINT meta=0 nullable=1 is_null=0 */"
        self.assertRegex(binlogmask.mask_values(str2, 0), r'###   @2=[0-9]+ /\* SHORTINT meta=0 nullable=1 is_null=0 \*/')

        str3 = "###   @3=0 /* MEDIUMINT meta=0 nullable=1 is_null=0 */"
        self.assertRegex(binlogmask.mask_values(str3, 0), r'###   @3=[0-9]+ /\* MEDIUMINT meta=0 nullable=1 is_null=0 \*/')

        str4 = "###   @4=0 /* INT meta=0 nullable=1 is_null=0 */"
        self.assertRegex(binlogmask.mask_values(str4, 0), r'###   @4=[0-9]+ /\* INT meta=0 nullable=1 is_null=0 \*/')

        str5 = "###   @5=0 /* LONGINT meta=0 nullable=1 is_null=0 */"
        self.assertRegex(binlogmask.mask_values(str5, 0), r'###   @5=[0-9]+ /\* LONGINT meta=0 nullable=1 is_null=0 \*/')

    def test_mask_blobs(self):
        binlogmask = binlogmaskmoj.BinlogMask()

        str1 = "###   @1='a' /* TINYBLOB/TINYTEXT meta=1 nullable=1 is_null=0 */"
        self.assertRegex(binlogmask.mask_values(str1, 0), r"###   @1='[A-Z0-9]+' /\* TINYBLOB/TINYTEXT meta=1 nullable=1 is_null=0 \*/")

        str2 = "###   @2='a' /* MEDIUMBLOB/MEDIUMTEXT meta=3 nullable=1 is_null=0 */"
        self.assertRegex(binlogmask.mask_values(str2, 0), r"###   @2='[A-Z0-9]+' /\* MEDIUMBLOB/MEDIUMTEXT meta=3 nullable=1 is_null=0 \*/")

        str3 = "###   @3='a' /* BLOB/TEXT meta=2 nullable=1 is_null=0 */"
        self.assertRegex(binlogmask.mask_values(str3, 0), r"###   @3='[A-Z0-9]+' /\* BLOB/TEXT meta=2 nullable=1 is_null=0 \*/")

        str4 = "###   @4='a' /* LONGBLOB/LONGTEXT meta=4 nullable=1 is_null=0 */"
        self.assertRegex(binlogmask.mask_values(str4, 0), r"###   @4='[A-Z0-9]+' /\* LONGBLOB/LONGTEXT meta=4 nullable=1 is_null=0 \*/")

    def test_mask_strings(self):
        binlogmask = binlogmaskmoj.BinlogMask()

        str1 = "###   @1='a' /* STRING(10) meta=65034 nullable=1 is_null=0 */"
        self.assertRegex(binlogmask.mask_values(str1, 0), r"###   @1='[A-Z0-9]' /\* STRING\(10\) meta=65034 nullable=1 is_null=0 \*/")

        str2 = "###   @2='b' /* VARSTRING(10) meta=10 nullable=1 is_null=0 */"
        self.assertRegex(binlogmask.mask_values(str2, 0), r"###   @2='[A-Z0-9]' /\* VARSTRING\(10\) meta=10 nullable=1 is_null=0 \*/")

    def test_mask_enum(self):
        binlogmask = binlogmaskmoj.BinlogMask()

        str1 = "###   @1=1 /* ENUM(1 byte) meta=63233 nullable=1 is_null=0 */"
        self.assertRegex(binlogmask.mask_values(str1, 0), r"###   @1=[0-9]+ /\* ENUM\(1 byte\) meta=63233 nullable=1 is_null=0 \*/")

    def test_mask_dates(self):
        binlogmask = binlogmaskmoj.BinlogMask()
        timeshift = random.randint(0, 60 * 60 * 24 * 365)

        str1 = "###   @1='2022:03:05' /* DATE meta=0 nullable=1 is_null=0 */"
        self.assertRegex(binlogmask.mask_values(str1, timeshift), r"###   @1='[0-9]{4}:[0-9]{2}:[0-9]{2}' /\* DATE meta=0 nullable=1 is_null=0 \*/")

        str2 = "###   @2=1646460296 /* TIMESTAMP(0) meta=0 nullable=0 is_null=0 */"
        self.assertRegex(binlogmask.mask_values(str2, timeshift), r"###   @2=[0-9]+ /\* TIMESTAMP\(0\) meta=0 nullable=0 is_null=0 \*/")
