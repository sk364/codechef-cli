# CodeChef CLI [![PyPI version](https://badge.fury.io/py/codechefcli.svg)](https://badge.fury.io/py/codechefcli) [![Build Status](https://travis-ci.org/sk364/codechef-cli.svg?branch=master)](https://travis-ci.org/sk364/codechef-cli)

A command-line tool for querying and submitting problems on [CodeChef](https://www.codechef.com/).

# Features
* Search & submit problems
* Search solutions
* Search users, ratings, tags and teams

# Requirements
* python (>= 3.6)
* [requests_html](https://github.com/psf/requests-html/) (0.10.0)

# Installation
```
pip install codechefcli
```

# Usage

```
# See full list of options:
codechefcli --help

# Login to CodeChef
codechefcli --login

# Get problem description:
codechefcli --problem WEICOM

# Get contests:
codechefcli --contests

# Submit a problem:
codechefcli --submit WEICOM /path/to/solution/file C++
```

# Linting & Testing

```
# run tests
pytest -v

# lint
isort
flake8 . --max-line-length=100
```
