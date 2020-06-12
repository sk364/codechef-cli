# -*- coding: utf-8 -*-

import sys
from codecs import open

from setuptools import setup

if sys.version < '3.6':
    print("This version is not supported.")
    sys.exit(1)

with open('README.rst') as f:
    longd = f'\n\n{f.read()}'

setup(
    name='codechefcli',
    include_package_data=True,
    packages=["codechefcli"],
    data_files=[('codechefcli', [])],
    entry_points={"console_scripts": ['codechefcli = codechefcli.__main__:main']},
    install_requires=['requests_html'],
    python_requires='>=3.6',
    version='0.5.1',
    url='http://www.github.com/sk364/codechef-cli',
    keywords="codechefcli codechef cli programming competitive-programming competitive-coding",
    license='GNU',
    author='Sachin Kukreja',
    author_email='skad5455@gmail.com',
    description='CodeChef Command Line Interface',
    long_description=longd
)
