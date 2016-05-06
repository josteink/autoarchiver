import unittest
import archive


class Tests(unittest.TestCase):
    def test_parse_dates(self):
        from datetime import datetime
        year = datetime.now().year
        syear = str(year)

        expected = datetime(year, 11, 30)

        testcases = [
            syear + "-11-30",
            "30/11/" + syear,
            "30/11"
        ]

        for testcase in testcases:
            result = archive.get_date_from_string(testcase)
            self.assertEqual(expected, result)
