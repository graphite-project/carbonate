import os
import re
from carbonate import __version__
from setuptools import setup, find_packages
from setuptools.command.install_scripts import install_scripts


class my_install_scripts(install_scripts):
    def write_script(self, script_name, contents, mode="t", *ignored):
        contents = re.sub("import sys",
                          "import sys\nsys.path.append('/opt/graphite/lib')",
                          contents)
        install_scripts.write_script(self, script_name, contents,
                                     mode="t", *ignored)


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="carbonate",
    version=__version__,
    author="Scott Sanders",
    author_email="scott@jssjr.com",
    description=("Tools for managing federated carbon clusters."),
    license="MIT",
    keywords="graphite carbon",
    url="https://github.com/jssjr/carbonate",
    include_package_data=True,
    packages=find_packages(),
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    install_requires=[
      "carbon",
      "whisper",
    ],
    cmdclass={'install_scripts': my_install_scripts},
    entry_points={
        'console_scripts': [
            'carbon-lookup = carbonate.cli:carbon_lookup',
            'carbon-sync = carbonate.cli:carbon_sync',
            'carbon-sieve = carbonate.cli:carbon_sieve',
            'carbon-list = carbonate.cli:carbon_list',
            'carbon-hosts = carbonate.cli:carbon_hosts',
            'carbon-path = carbonate.cli:carbon_path',
            'carbon-stale = carbonate.cli:carbon_stale',
            'whisper-fill = carbonate.cli:whisper_fill',
            'whisper-aggregate = carbonate.cli:whisper_aggregate'
        ]
    },
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ]
)
