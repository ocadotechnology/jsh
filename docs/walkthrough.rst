CLI Walkthrough
===============

This document walks you through building a more advanced CLI than that shown in
the Basic Usage section.

Help Text
---------

We'll start with the JSH layout from the Basic Usage section, and add some more
descriptive help text to describe the ``exit`` command. To do so, you need to
turn ``exit`` into a dictionary:

.. code-block:: python

    layout =  {
        'exit': {
            '?': 'Quit this silly application',
            None: jsh.exit,
        },
    }

The action to take when Enter is pressed after typing the command is defined under
the ``None`` key, and the help text is defined under ``'?'``.

This makes the help look like this:

::

    > ?
    Possible completions:
      exit   Quit this silly application


Custom Handlers and Multi-Word Commands
---------------------------------------

The CLI would be useless without the ability to define your own methods to run
when a command is submitted. Let's now add some commands with more than one word,
and some custom handlers. We'll define two commands, ``show version`` and ``show
pid``. First, we'll need to write the functions to handle them. When executed, these
functions will be passed a single argument, the ``JSH`` instance.

.. code-block:: python

    import os

    def show_version(cli):
        print 'Useless CLI version 0.0.1'

    def show_pid(cli):
        print 'My PID is {0}'.format(os.getpid())

Now we'll add these to the layout, along with some help text. The individual words
in the commands will correspond to levels in the layout tree:

.. code-block:: python

    layout = {
        'show': {
            '?': 'Display various information',
            'pid': {
                '?': 'Display my PID',
                None: show_pid,
            },
            'version': {
                '?': 'Display my version',
                None: show_version,
            },
        },
        'exit': {
            '?': 'Quit this silly application',
            None: jsh.exit,
        },
    }

Now our CLI looks like this:

::

    > ?
    Possible completions:
      exit   Quit this silly application
      show   Display various information
    > show ?
    Possible completions:
      pid       Display my PID
      version   Display my version
    > show
    Incomplete command 'show'
    > show pid ?
    Possible completions:
      <[Enter]>   Execute this command
    > show pid
    My PID is 4633
    > show version
    Useless CLI version 0.0.1
    >

Notice how the command ``show`` by itself is not allowed? This is because there is
no ``None`` key under the ``show`` level of the layout tree - the CLI does not know
what to do if that is the only command entered.

Command Variables
-----------------

Often, your CLI will need to accept a variable from the user - something you cannot
know in advance. To demonstrate how this is possible with JSH, we'll add some shopping
list functionality: adding items to the list, viewing the list and removing items
from the list.

Viewing the list is easy:

.. code-block:: python

    shopping_list = []

    def show_list(cli):
        if not shopping_list:
            print 'Shopping list is empty'
        else:
            print 'Items:'
            print '\n'.join(shopping_list)

    layout = {
        ...
        'show': {
            ...
            'list': {
                '?': 'Display shopping list',
                None: show_list,
            }
            ...
        },
        ...
    }

Adding items is just as easy, but this time the handler function will be passed
another argument - whatever the user typed on the command line at that point:

.. code-block:: python

    def add_item(cli, item):
        shopping_list.append(item)

Adding the following to the layout will implement the ``add item <name>`` command:

.. code-block:: python

    layout = {
        ...
        'add': {
            '?': 'Add stuff',
            'item': {
                '?': 'Add item to shopping list',
                str: {
                    '?': ('item', 'Item description'),
                    None: add_item,
                },
            },
        },
        ...
    }

Let's take a look at the new stuff introduced. Using ``str`` as a key says that
the parser should expect an arbitrary string at this point in the command. Pressing
Enter after the arbitrary string will run the ``add_item`` function with two arguments:
the ``JSH`` instance and the arbitrary string entered by the user. Also notice that
the help text is now a tuple with the descriptive text as the second element - the
first element is a metavariable, and you will see how this is used below.

Our CLI now looks like this:

::

    > show ?
    Possible completions:
      list      Display shopping list
      pid       Display my PID
      version   Display my version
    > show list
    Shopping list is empty
    > add ?
    Possible completions:
      item   Add item to shopping list
    > add item ?
    Possible completions:
      <item>   Item description
    > add item carrots ?
    Possible completions:
      <[Enter]>   Execute this command
    > add item carrots
    > add item courgettes
    > show list
    Items:
    carrots
    courgettes
    >

Custom Completion
-----------------

Now for our command to remove items from the list. Here's the function to do it:

.. code-block:: python

    def remove_item(cli, item):
        try:
            shopping_list.remove(item)
        except ValueError:
            print 'Item not in list'

    layout = {
        ...
        'remove': {
            '?': 'Get rid of stuff',
            'item': {
                '?': 'Remove item to shopping list',
                str: {
                    '?': ('item', 'Item to remove'),
                    None: remove_item,
                },
            },
        },
        ...
    }

Now our CLI shows:

::

    > add item bananas
    > add item oranges
    > add item strawberries
    > show list
    Items:
    bananas
    oranges
    strawberries
    > remove ?
    Possible completions:
      item   Remove item from shopping list
    > remove item ?
    Possible completions:
      <item>   Item to remove
    > remove item apples
    Item not in list
    > remove item oranges
    > show list
    Items:
    bananas
    strawberries
    >

That works, but it would be great if we could offer completion of items that have
already been added to the list when removing them... and we can! First, we need a
function to provide a list of the items in the shopping list (again, it takes the
``JSH`` instance as the first argument, and any arbitrary arguments that preceed
it in the command - in this case, none). As we're storing our shopping list as a
``list`` already, this is pretty easy:

.. code-block:: python

    def complete_items(cli):
        return shopping_list

And now we integrate this into the layout using the ``'\t'`` key, which signifies
that this function should be called when searching for a list of valid completions:

.. code-block:: python

    layout = {
        ...
        'remove': {
            '?': 'Get rid of stuff',
            'item': {
                '?': 'Remove item from shopping list',
                '\t': complete_items,
                str: {
                    '?': ('item', 'Item to remove'),
                    None: remove_item
                },
            },
        },
        ...
    }

Finally, the items already in the shopping list appear in the list of possible
completions when removing an item:

::

    > add item carrots
    > add item courgettes
    > add item beetroot
    > show list
    Items:
    carrots
    courgettes
    beetroot
    > remove item ?
    Possible completions:
      <item>       Item to remove
      beetroot
      carrots
      courgettes
    > remove item c?
    Possible completions:
      <item>       Item to remove
      carrots
      courgettes
    > remove item carrots
    > show list
    Items:
    courgettes
    beetroot
    >

.. note::

    It's also possible for the completion function to return a dictionary. In this
    case, the keys are the possible completions and the values are used as descriptions
    in the help output.

And that's it - you've built your first CLI with JSH, and it wasn't all that hard.
Check out the other options available to you by reading the rest of this documentation.




