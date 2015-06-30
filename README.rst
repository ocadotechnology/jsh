=================================
jsh - a Junos-style CLI library
=================================

.. image:: https://img.shields.io/travis/ocadotechnology/jsh.svg
   :target: https://travis-ci.org/ocadotechnology/jsh
   :alt: Build Status
.. image:: https://landscape.io/github/ocadotechnology/jsh/master/landscape.svg?style=flat
   :target: https://landscape.io/github/ocadotechnology/jsh/master
   :alt: Code Health Badge
.. image:: https://readthedocs.org/projects/jsh/badge/?version=latest
   :target: http://jsh.readthedocs.org/en/latest/
   :alt: Documentation Status
.. image:: https://img.shields.io/pypi/v/jsh.svg
   :target: https://pypi.python.org/pypi/jsh/
   :alt: Version Badge
.. image:: https://img.shields.io/pypi/l/jsh.svg
   :target: https://pypi.python.org/pypi/jsh/
   :alt: License Badge

**JSH** is a Junos-inspired CLI library for your Python apps.
If you've ever logged into a Junos_ device, you'll know how good the CLI is.
It offers:

- tab-completion, including completion of names of items in the config
- help by pressing "?" at any point
- completion on pressing either space, tab or enter

JSH attempts to reproduce some of these features (and others) in a Python library
based on Readline, to allow you to build better quality CLIs for your apps.

Documentation
=============

Full documentation can be found at RTD_.

Installation
============

Install from PyPI using ``pip install jsh``.

Basic Usage
===========

The library takes a CLI "layout", which is a dictionary-based tree structure
describing your CLI commands. For example, a completely useless CLI with
just an ``exit`` command, you would define it like this:

.. code-block:: python

    import jsh

    layout = {
        'exit': jsh.exit,
    }

    cli = jsh.JSH(layout)

    while True:
        try:
            cli.read_and_execute()
        except jsh.JSHError as err:
            print err
        except EOFError:
            break

This creates a basic layout with a single available command (``exit``), passes
it to an instance ``jsh.JSH``, and starts an infinite loop, using the ``read_and_execute``
method of the ``JSH`` CLI object to interact with the user.

This provides a CLI that looks like the following:

::

    > ?
    Possible completions:
      exit
    > ex?
    Possible completions:
      exit
    > exit ?
    Possible completions:
      <[Enter]>   Execute this command
    > exit

.. _Junos: http://www.juniper.net/us/en/products-services/nos/junos/
.. _RTD: http://jsh.readthedocs.org/en/latest/
