import os
import pwd
import unittest

from carbonate import config


class ConfigTest(unittest.TestCase):

    simple_config = "tests/conf/simple.conf"
    real_config = "tests/conf/realistic.conf"

    def test_config_replication_factor(self):
        c = config.Config(self.simple_config)

        self.assertEqual(c.replication_factor(), 1)

    def test_config_destinations(self):
        c = config.Config(self.simple_config)

        expected = ['1.1.1.1:2003:0', '2.2.2.2:2003:0']
        self.assertEqual(c.destinations(), expected)

    def test_config_multiple_clusters(self):
        c = config.Config(self.real_config)

        expected = ['main', 'standalone', 'fnv']
        self.assertEqual(set(c.clusters()), set(expected))

    def test_config_ssh_user(self):
        c = config.Config(self.real_config)

        expected = 'carbonate'
        self.assertEqual(c.ssh_user('standalone'), expected)

    def test_config_ssh_user_default(self):
        c = config.Config(self.simple_config)

        expected = pwd.getpwuid(os.getuid()).pw_name
        self.assertEqual(c.ssh_user(), expected)

    def test_config_hashing_type(self):
        c = config.Config(self.real_config)

        expected = 'fnv1a_ch'
        self.assertEqual(c.hashing_type('fnv'), expected)

    def test_config_hashing_type_default(self):
        c = config.Config(self.simple_config)

        expected = 'carbon_ch'
        self.assertEqual(c.hashing_type(), expected)
