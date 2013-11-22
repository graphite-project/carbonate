import socket
import argparse


def local_addresses():
    ips = socket.gethostbyname_ex(socket.gethostname())[2]
    return set([ip for ip in ips if not ip.startswith("127.")][:1])


def common_parser(description='untitled'):
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        '-c', '--config-file',
        default='/opt/graphite/conf/carbonate.conf',
        help='Config file to use')

    parser.add_argument(
        '-C', '--cluster',
        default='main',
        help='Cluster name')

    return parser
