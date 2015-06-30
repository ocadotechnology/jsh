Sections
========

Another feature, inspired not by the Junos CLI, but by the F5_ CLI is sections.
Sections let the user focus on a particular part of the CLI. Taking the example
from the walkthrough, we can focus on the items in the shopping list.

Let's add some commands to our layout to handle this:

.. code-block:: python

    layout = {
        '/': {
            '?': 'Go to top level',
            None: jsh.set_section(None)
        },
        '/item': {
            '?': 'Work on items',
            None: jsh.set_section('item')
        },
        'add': {
            '?': 'Add stuff',
            'item': {
                '?': 'Add item to shopping list',
                str: {
                    '?': ('item', 'Item description'),
                    None: add_item
                }
            }
        },
        'remove': {
            '?': 'Get rid of stuff',
            'item': {
                '?': 'Remove item from shopping list',
                '\t': complete_items,
                str: {
                    '?': ('item', 'Item to remove'),
                    None: remove_item
                }
            }
        },
        'show': {
            '?': 'Display various information',
            'list': {
                '?': 'Display shopping list',
                None: show_list
            },
            'pid': {
                '?': 'Display my PID',
                None: show_pid
            },
            'version': {
                '?': 'Display my version',
                None: show_version
            }
        },
        'exit': {
            '?': 'Quit this silly application',
            None: jsh.exit
        }
    }

This now lets us interact with the CLI like this:

::

    > ?
    Possible completions:
      /        Go to top level
      /item    Work on items
      add      Add stuff
      exit     Quit this silly application
      remove   Get rid of stuff
      show     Display various information
    > add ?
    Possible completions:
      item   Add item to shopping list
    > /item
    > add ?
    Possible completions:
      <item>   Item description
    > add carrots
    > add potatoes
    > show list
    Items:
    carrots
    potatoes
    > remove potatoes
    > show list
    Items:
    carrots
    >

Being inside the "item" section means that we can (and, in fact, must)
miss out the second word of a command when that word is ``item``.

Finally, it would be nice if the CLI told us which section we are currently
in.  We can do this by customising the prompt and including the string
``{section}`` in it, which will be replaced by the name of the current
section:

.. code-block:: python

    cli = jsh.JSH(
        layout,
        prompt='shopping{section}> '
    )

This gives us this:

::

    shopping> /item
    shopping(item)> /
    shopping>

We can customise the brackets around the section name, for example:

.. code-block:: python

    cli = jsh.JSH(
        layout,
        prompt='shopping{section}> ',
        section_delims=('/', '')
    )

This gives:

::

    shopping> /item
    shopping/item> /
    shopping>

However, section support is quite basic at the moment and needs more work.
It's currently nowhere near what the F5 CLI does.

.. _F5: https://f5.com/products/big-ip
