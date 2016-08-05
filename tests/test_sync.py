import unittest
import os
import whisper
import time
import random

from carbonate.sync import heal_metric


class SyncTest(unittest.TestCase):

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


    def test_heal_empty(self):
        testdb = "test-%s" % self.db
        self._removedb()

        try:
            os.unlink(testdb)
        except (IOError, OSError):
            pass

        schema = [(1, 20)]
        emptyData = []
        self._createdb(self.db, schema)
        self._createdb(testdb, schema, emptyData)

        heal_metric(self.db, testdb)

        original_data = whisper.fetch(self.db, 0)
        filled_data = whisper.fetch(testdb, 0)
        self.assertEqual(original_data, filled_data)

        # Heal again, should still be equal
        heal_metric(self.db, testdb)
        filled_data = whisper.fetch(testdb, 0)
        self.assertEqual(original_data, filled_data)


    def test_heal_target_corrupt(self):
        testdb = "/dev/null"
        self._removedb()

        schema = [(1, 20)]
        self._createdb(self.db, schema)
        original_data = whisper.fetch(self.db, 0)

        # This should log complaints but exit successfully as it cannot
        # heal its target /dev/null
        heal_metric(self.db, testdb)
        data = whisper.fetch(self.db, 0)
        self.assertEqual(original_data, data)


    def test_heal_target_missing(self):
        testdb = "test-%s" % self.db
        try:
            os.unlink(testdb)
        except (IOError, OSError):
            pass

        self._removedb()

        schema = [(1, 20)]
        self._createdb(self.db, schema)
        original_data = whisper.fetch(self.db, 0)

        # This should log complaints but exit successfully as it cannot
        # heal its target /dev/null
        heal_metric(self.db, testdb)
        data = whisper.fetch(testdb, 0)
        self.assertEqual(original_data, data)


    def test_heal_source_corrupt(self):
        testdb = "/dev/null"
        self._removedb()

        schema = [(1, 20)]
        self._createdb(self.db, schema)
        original_data = whisper.fetch(self.db, 0)

        # This should log complaints but exit successfully as it cannot
        # read from the source /dev/null
        heal_metric(testdb, self.db)
        data = whisper.fetch(self.db, 0)
        self.assertEqual(original_data, data)


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
