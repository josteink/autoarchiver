# -*- coding: utf-8 -*-

import unittest
import archive
from datetime import date


class Tests(unittest.TestCase):
    def test_parse_dates(self):
        year = date.today().year
        syear = str(year)

        expected = date(year, 1, 30)

        testcases = [
            syear + "-01-30",
            "30/01/" + syear,
            "30/01"
        ]

        for testcase in testcases:
            result = archive.get_date_from_string(testcase)
            self.assertEqual(expected, result)

    def test_parse_difficult_dates(self):
        testcase = "hjghkjd 13012016 fshdfhkds"
        expected = date(2016, 1, 13)

        result = archive.get_date_from_string(testcase)
        self.assertEqual(expected, result)

        testcase = "19/04/2013 12 15"
        expected = date(2013, 4, 19)
        result = archive.get_date_from_string(testcase)
        # not_expected = date(2013, 12, 15)
        # self.assertUnequal(not_expected, result)
        self.assertEqual(expected, result)

    def test_parse_non_date(self):
        # this ended getting parsed as $year-04-23 !!
        testcase = "ART. NR 30011832 22304"
        result = archive.get_date_from_string(testcase)
        self.assertEqual(None, result)

    def test_parse_path_as_date(self):
        testcase = "/home/jostein/DocumentArchive/2012/01/28/hp photosmart 5510 5515 all in one printer ink/result.txt"
        expected = date(2012, 1, 28)
        result = archive.get_date_from_string(testcase)
        self.assertEqual(expected, result)

    def test_ml_implementation(self):
        import ml_generate
        import os
        print(os.path.curdir)
        # having date in filename aids creating "decent" relative
        # time-offsets to content
        testcase = "./test-data/ml_validation_2013_04_19.txt"
        expected = date(2013, 4, 19)
        result = ml_generate.determine_date(testcase)
        self.assertEqual(expected, result)


if __name__ == "__main__":
    unittest.main()
