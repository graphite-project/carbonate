import fileinput
import os
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


def metrics_from_args(args):
    arg = args.metrics_file
    fi = arg if (arg and arg[0] != '-') else []
    return map(lambda s: s.strip(), fileinput.input(fi))


def metric_to_fs(path, prepend=None):
    filepath = path.replace('.', '/') + "." + "wsp"
    if prepend:
        filepath = os.path.join(prepend, filepath)
    return filepath


def fs_to_metric(path, prepend=None):
    if prepend:
        path = path.replace(prepend, '')
    return path.replace('.wsp', '').replace('/', '.').strip('.')
