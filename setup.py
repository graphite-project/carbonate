import os
from carbonate import __version__
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="carbonate",
    version=__version__,
    author="Scott Sanders",
    author_email="scott@jssjr.com",
    description=("Tools for managing federated carbon clusters."),
    license = "MIT",
    keywords = "graphite carbon",
    url = "https://github.com/jssjr/carbonate",
    include_package_data = True,
    packages=find_packages(),
    long_description = read('README.md'),
    install_requires = [
      "carbon",
      "whisper",
    ],
    entry_points = {
        'console_scripts': [
            'carbon-lookup = carbonate.cli:carbon_lookup',
            'carbon-sync = carbonate.cli:carbon_sync',
            'carbon-sieve = carbonate.cli:carbon_sieve',
            'carbon-list = carbonate.cli:carbon_list',
            'carbon-hosts = carbonate.cli:carbon_hosts',
            'whisper-fill = carbonate.cli:whisper_fill',
            'whisper-aggregate = carbonate.cli:whisper_aggregate'
            ]
        }
    )
