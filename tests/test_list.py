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

    expected_metrics_withsym = ["foo.sprockets",
                                "foo.widgets",
                                "ham.bones",
                                "ham.hocks",
                                "bar.sprockets",
                                "bar.widgets"]

    symlinks = [("foo", "bar"),]

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
        for s in cls.symlinks:
            os.symlink(os.path.join(cls.rootdir, s[0]), os.path.join(cls.rootdir, s[1]))

    def test_list_withsym(self):
        res = sorted(list(listMetrics(self.rootdir, True)))
        self.assertEqual(res, self.expected_metrics_withsym)

    def test_list_with_trailing_slash_withsym(self):
        res = sorted(list(listMetrics(self.rootdir + '/', True)))
        self.assertEqual(res, self.expected_metrics_withsym)

    def test_list(self):
        res = sorted(list(listMetrics(self.rootdir)))
        self.assertEqual(res, self.expected_metrics)

    def test_list_with_trailing_slash(self):
        res = sorted(list(listMetrics(self.rootdir + '/')))
        self.assertEqual(res, self.expected_metrics)

    @classmethod
    def tearDownClass(cls):
        os.system("rm -rf %s" % cls.rootdir)

