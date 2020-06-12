# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
import sys
from codecs import open

if sys.version < '2.0.0':
    print("Python 1 not supported...")
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
    python_requires='>=2.7',
    version='0.4.3',
    url='http://www.github.com/sk364/codechef-cli',
    keywords="codechefcli codechef cli programming competitive-programming competitive-coding",
    license='GNU',
    author='Sachin Kukreja',
    author_email='skad5455@gmail.com',
    description='CodeChef Command Line Interface',
    long_description=longd
)
