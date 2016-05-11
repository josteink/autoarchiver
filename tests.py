
import unittest
import archive


class Tests(unittest.TestCase):
    def test_parse_dates(self):
        from datetime import datetime
        year = datetime.now().year
        syear = str(year)

        expected = datetime(year, 1, 30)

        testcases = [
            syear + "-01-30",
            "30/01/" + syear,
            "30/01"
        ]

        for testcase in testcases:
            result = archive.get_date_from_string(testcase)
            self.assertEqual(expected, result)

    def test_parse_difficult_dates(self):
        from datetime import datetime

        testcase = "hjghkjd 13012016 fshdfhkds"
        expected = datetime(2016, 1, 13)

        result = archive.get_date_from_string(testcase)
        self.assertEqual(expected, result)

    def test_parse_non_date(self):
        # this ended getting parsed as $year-04-23 !!
        testcase = "ART. NR 30011832 22304"
        result = archive.get_date_from_string(testcase)
        self.assertEqual(None, result)

    def test_parse_path_as_date(self):
        from datetime import datetime
        testcase = "/home/jostein/DocumentArchive/2012/01/28/hp photosmart 5510 5515 all in one printer ink/result.txt"
        expected = datetime(2012,1,28)
        result = archive.get_date_from_string(testcase)
        self.assertEqual(expected, result)

if __name__ == "__main__":
    unittest.main()
