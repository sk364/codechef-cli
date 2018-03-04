# CodeChef CLI [![PyPI version](https://badge.fury.io/py/codechefcli.svg)](https://badge.fury.io/py/codechefcli) [![Build Status](https://api.travis-ci.org/sk364/codechef-cli.svg?branch=master)](https://api.travis-ci.org/sk364/codechef-cli)

A command-line tool for querying and submitting problems on [CodeChef](https://www.codechef.com/).

# Features

* Get problem description
* Get user information
* Submit problems
* Search problems in contest, by category, or by tags
* Get ratings
* Get problem solutions
* Get contests


# Installation

Available on pip. Install using the command:

> pip install codechefcli


# Usage

See full list of options:  
> codechefcli --help

Get problem description:  
> codechefcli --problem WEICOM

Get contests:  
> codechefcli --contests

Submit a problem:  
> codechefcli --submit WEICOM /path/to/solution/file C++
