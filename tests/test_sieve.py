import unittest
import carbonate.sieve


class FilterTest(unittest.TestCase):

    def setUp(self):
        config_file = "tests/conf/simple.conf"
        config = carbonate.config.Config(config_file)
        self.cluster = carbonate.cluster.Cluster(config)

    def test_sieve(self):
        inputs = ['metric.100',
                  'metric.101',
                  'metric.102',
                  'metric.103',
                  'metric.104',
                  'metric.105',
                  'metric.106',
                  'metric.107',
                  'metric.108',
                  'metric.109']

        node = '1.1.1.1'
        node_long = '1.1.1.1:2003:0'
        output = ['metric.101',
                  'metric.102',
                  'metric.103',
                  'metric.105',
                  'metric.107',
                  'metric.108']

        node2 = '2.2.2.2'
        node2_long = '2.2.2.2:2003:0'
        output2 = ['metric.100',
                  'metric.104',
                  'metric.106',
                  'metric.109']

        f = list(carbonate.sieve.filterMetrics(inputs, node, self.cluster))
        self.assertEqual(f, output)
        f = list(carbonate.sieve.filterMetrics(inputs, node_long, self.cluster))
        self.assertEqual(f, output)

        f = list(carbonate.sieve.filterMetrics(inputs, node2, self.cluster))
        self.assertEqual(f, output2)
        f = list(carbonate.sieve.filterMetrics(inputs, node2_long, self.cluster))
        self.assertEqual(f, output2)

        f = list(carbonate.sieve.filterMetrics(inputs, node, self.cluster, True))
        self.assertEqual(f, output2)

        f = list(carbonate.sieve.filterMetrics(inputs, node2, self.cluster, True))
        self.assertEqual(f, output)

