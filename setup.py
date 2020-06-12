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
    longd = f.read()

setup(
    name='codechefcli',
    include_package_data=True,
    packages=["codechefcli", "codechefcli.utils"],
    data_files=[('codechefcli', []), ('codechefcli.utils', [])],
    entry_points={"console_scripts": ['codechefcli = codechefcli.__main__:main']},
    install_requires=['BeautifulSoup4', 'requests'],
    python_requires='>=2.7',
    requires=['BeautifulSoup4', 'requests'],
    version='0.4.2',
    url='http://www.github.com/sk364/codechef-cli',
    keywords="codechefcli codechef cli programming",
    license='GNU',
    author='Sachin Kukreja',
    author_email='skad5455@gmail.com',
    description='CodeChef command line interface. CodeChefCLI helps competitive coders to search, view,\
                 and submit problems in CodeChef.',
    long_description="\n\n"+longd
)
