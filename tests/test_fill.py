import unittest
import os
import whisper
import time
import random

from carbonate.fill import fill_archives


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
        data = [None]*20
        emptyData = [data]
        startTime = time.time()
        self._createdb(self.db, schema)
        self._createdb(testdb, schema, emptyData)

        fill_archives(self.db, testdb, startTime)

        original_data = whisper.fetch(self.db, 0)
        filled_data = whisper.fetch(testdb, 0)
        self.assertEqual(original_data, filled_data)

    def test_fill_should_override_destination(self):
        testdb = "test-%s" % self.db
        self._removedb()

        try:
            os.unlink(testdb)
        except (IOError, OSError):
            pass

        schema = [(1, 20)]
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
        emptyData = [data]
        startTime = time.time()
        self._createdb(self.db, schema)
        self._createdb(testdb, schema, emptyData)

        fill_archives(self.db, testdb, startTime)

        original_data = whisper.fetch(self.db, 0)
        filled_data = whisper.fetch(testdb, 0)
        self.assertEqual(original_data, filled_data)

    def test_fill_should_handle_gaps(self):
        testdb = "test-%s" % self.db
        self._removedb()

        try:
            os.unlink(testdb)
        except (IOError, OSError):
            pass

        schema = [(1, 20)]
        data = [1, 2, 3, 4, 5, 6, None, None, None, None,
                11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
        emptyData = [data]
        startTime = time.time()
        self._createdb(self.db, schema)
        self._createdb(testdb, schema, emptyData)

        fill_archives(self.db, testdb, startTime)

        original_data = whisper.fetch(self.db, 0)
        filled_data = whisper.fetch(testdb, 0)
        self.assertEqual(original_data, filled_data)

    def _createdb(self, wsp, schema=[(1, 20)], data=None):
        whisper.create(wsp, schema)
        if data is None:
            tn = time.time() - 20
            data = []
            for i in range(20):
                data.append((tn + 1 + i, random.random() * 10))
        whisper.update_many(wsp, data[1:])
        return data

    @classmethod
    def tearDownClass(cls):
        try:
            cls._removedb()
            os.unlink("test-%s" % cls.db)
        except (IOError, OSError):
            pass
