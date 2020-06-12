CodeChef CLI |PyPI version| |Build Status|
==========================================

A command-line tool for querying and submitting problems on `CodeChef`_.

Features
========

-  Get problem description
-  Get user information
-  Submit problems
-  Search problems in contest, by category, or by tags
-  Get ratings
-  Get problem solutions
-  Get contests

Installation
============

Available on pip. Install using the command:

   pip install codechefcli

Usage
=====

See full list of options:

   codechefcli --help

Get problem description:

   codechefcli --problem WEICOM

Get contests:

   codechefcli --contests

Submit a problem:

   codechefcli --submit WEICOM /path/to/solution/file C++

.. _CodeChef: https://www.codechef.com/

.. |PyPI version| image:: https://badge.fury.io/py/codechefcli.svg
   :target: https://badge.fury.io/py/codechefcli
.. |Build Status| image:: https://api.travis-ci.org/sk364/codechef-cli.svg?branch=master
   :target: https://api.travis-ci.org/sk364/codechef-cli