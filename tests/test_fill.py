import unittest
import os
import whisper
import time
import random

import mock

from carbonate.fill import fill_archives

def _average(ints_or_nones):
    total = 0
    count = 0
    for i in ints_or_nones:
        if i is not None:
            total += i
            count += 1
    return total // count


class FillTest(unittest.TestCase):

    db = "db.wsp"

    @classmethod
    def setUpClass(cls):
        cls._removedb()

    @classmethod
    def _removedb(cls):
        try:
            if os.path.exists(cls.db):
                os.unlink(cls.db)
        except (IOError, OSError):
            pass


    def test_fill_empty(self):
        testdb = "test-%s" % self.db
        self._removedb()

        try:
            os.unlink(testdb)
        except (IOError, OSError):
            pass

        schema = [(1, 20)]
        emptyData = []
        startTime = time.time()
        self._createdb(self.db, schema)
        self._createdb(testdb, schema, emptyData)

        fill_archives(self.db, testdb, startTime)

        original_data = whisper.fetch(self.db, 0)
        filled_data = whisper.fetch(testdb, 0)
        self.assertEqual(original_data, filled_data)


    def test_fill_should_not_override_destination(self):
        testdb = "test-%s" % self.db
        self._removedb()

        try:
            os.unlink(testdb)
        except (IOError, OSError):
            pass

        schema = [(1, 20)]
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                11, 12, 13, 14, 15, 16, 17, 18, 19, 20]

        end = int(time.time()) + schema[0][0]
        start = end - (schema[0][1] * schema[0][0])
        times = range(start, end, schema[0][0])

        override_data = zip(times, data)

        startTime = time.time()
        self._createdb(self.db, schema)
        self._createdb(testdb, schema, override_data)

        fill_archives(self.db, testdb, startTime)

        filled_data = whisper.fetch(testdb, 0)
        self.assertEqual(data, filled_data[1])


    def test_fill_should_handle_gaps(self):
        testdb = "test-%s" % self.db
        self._removedb()

        try:
            os.unlink(testdb)
        except (IOError, OSError):
            pass

        schema = [(1, 20)]
        complete = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                    11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
        original = [91, # make sure only null values are filled
                2, 3,
                4,
                5,
                6,
                7, 8, 9, 10,
                11, 12, 13, 14, 15, 16, 17, 18, None,  # empty value doesn't overwrite
                20,
                ]
        holes = [1,
                None, None,  # multiple concecutive missing data points
                4,
                None, # single missing data point
                6,
                None, None, None, None,
                11, 12, 13, 14, 15, 16, 17, 18, 19,
                None, # trailing missing data point
                ]

        end = int(time.time()) + schema[0][0]
        start = end - (schema[0][1] * schema[0][0])
        times = range(start, end, schema[0][0])

        original_data = [t for t in zip(times, original) if t[1] is not None]
        holes_data = [t for t in zip(times, holes) if t[1] is not None]
        self._createdb(self.db, schema, original_data)
        self._createdb(testdb, schema, holes_data)

        fill_archives(self.db, testdb, time.time())

        filled_data = whisper.fetch(testdb, 0)
        self.assertEqual(complete, filled_data[1])

    @mock.patch('time.time', return_value=123456)
    def test_fill_endat(self, unused_mock_time):
        dst_db = "dst-%s" % self.db
        self._removedb()
        try:
            os.unlink(dst_db)
        except (IOError, OSError):
            pass

        complete = range(1, 21)
        seconds_per_point = 1
        seconds_per_point_l2 = seconds_per_point * 4
        points_number = len(complete)
        schema = [(seconds_per_point, points_number),
                  (seconds_per_point_l2, points_number),
        ]
        empty_data = []

        end = int(time.time()) + seconds_per_point
        start = end - (points_number * seconds_per_point)
        times = range(start, end, seconds_per_point)

        complete_data = zip(times, complete)
        self._createdb(self.db, schema, complete_data)
        self._createdb(dst_db, schema, empty_data)

        quarter = points_number // 4
        half = points_number // 2
        three_quarter =  points_number * 3 // 4

        # fills a fourth of data, from 2/4th to 3/4th
        fill_archives(self.db, dst_db, time.time()-quarter, time.time()-half)
        quarter_filled_data = whisper.fetch(dst_db, start-seconds_per_point)[1]
        expected = [None]*half + complete[half:three_quarter] + [None]*quarter
        self.assertEqual(expected, quarter_filled_data)
        # Fetching data older than start forces the use of the second level of aggregation
        # We get a first empty cell and then
        quarter_filled_data_l2 = whisper.fetch(dst_db, 0)[1]
        average_l1 = _average(quarter_filled_data)
        average_l2 = _average(quarter_filled_data_l2)
        self.assertEqual(average_l1, average_l2)

        # fills a half of data, from 2/4th to 4/4th
        fill_archives(self.db, dst_db, time.time(), time.time()-half)
        half_filled_data = whisper.fetch(dst_db, start-seconds_per_point)[1]
        expected = [None]*half + complete[half:]
        self.assertEqual(expected, half_filled_data)

        # Explicitly passes the default value of endAt=now (excluded)
        fill_archives(self.db, dst_db, time.time(), endAt=0)
        filled_data = whisper.fetch(dst_db, start-seconds_per_point)[1]
        self.assertEqual(complete[:-1], filled_data[:-1])
        self.assertEqual(filled_data[-1], None)


    def _createdb(self, wsp, schema=[(1, 20)], data=None):
        whisper.create(wsp, schema)
        if data is None:
            tn = time.time() - 20
            data = []
            for i in range(20):
                data.append((tn + 1 + i, random.random() * 10))
        whisper.update_many(wsp, data)
        return data

    @classmethod
    def tearDownClass(cls):
        try:
            cls._removedb()
            os.unlink("test-%s" % cls.db)
        except (IOError, OSError):
            pass
