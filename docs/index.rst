Welcome to JSH's documentation
==============================================

**JSH** is a Junos-inspired CLI library for your Python apps.
If you've ever logged into a Junos_ device, you'll know how good the CLI is.
It offers:

- tab-completion, including completion of names of items in the config
- help by pressing "?" at any point
- completion on pressing either space, tab or enter

JSH attempts to reproduce some of these features (and others) in a Python library
based on Readline, to allow you to build better quality CLIs for your apps.

Requirements
============

* Python 2.6+

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

Full Documentation
==================

.. toctree::
 :maxdepth: 2

 walkthrough
 options
 validators
 sections
 clioptions

.. _Junos: http://www.juniper.net/us/en/products-services/nos/junos/
