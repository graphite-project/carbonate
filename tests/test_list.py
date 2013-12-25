import os
import unittest

from carbonate.list import listMetrics


class ListTest(unittest.TestCase):

    metrics_tree = ["foo",
                    "foo/sprockets.wsp",
                    "foo/widgets.wsp",
                    "ham",
                    "ham/bones.wsp",
                    "ham/hocks.wsp"]

    expected_metrics = ["foo.sprockets",
                        "foo.widgets",
                        "ham.bones",
                        "ham.hocks"]

    rootdir = os.path.join(os.curdir, 'test_storage')

    @classmethod
    def setUpClass(cls):
        os.system("rm -rf %s" % cls.rootdir)
        os.mkdir(cls.rootdir)
        for f in cls.metrics_tree:
            if f.endswith('wsp'):
                open(os.path.join(cls.rootdir, f), 'w').close()
            else:
                os.mkdir(os.path.join(cls.rootdir, f))

    def test_list(self):
        res = list(listMetrics(self.rootdir))
        self.assertEqual(res, self.expected_metrics)

    def test_list_with_trailing_slash(self):
        res = list(listMetrics(self.rootdir + '/'))
        self.assertEqual(res, self.expected_metrics)

    @classmethod
    def tearDownClass(cls):
        os.system("rm -rf %s" % cls.rootdir)
