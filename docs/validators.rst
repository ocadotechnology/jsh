Validators
==========

JSH provides the following built-in validators for use with the ``_validate`` option.

.. attribute:: validate_int

    Validates that the provided string is an integer.

    .. code-block:: python

        import jsh

        def print_num(cli, num):
            print 'User entered {}'.format(num)

        layout = {
            ...
            'num': {
                '?': 'A number',
                'str': {
                    '?': ('num', 'A number'),
                    '_validate': jsh.validate_int,
                    None, print_num,
                },
            },
            ...
        }

    Produces the following CLI:

    ::

        > ?
        Possible completions:
          num    Enter a number
        > num ?
        Possible completions:
          num       A number
        > number foo
        Invalid argument: 'foo' is not a valid integer.
        > num 5
        User entered 5
        >

.. attribute:: validate_range(min, max)

    Validates that the provided string is an integer in a given range. Takes two
    integer arguments ``min`` and ``max`` which the entered integer must be between
    (inclusive).

    .. code-block:: python

        import jsh

        def print_num(cli, num):
            print 'User entered {}'.format(num)

        layout = {
            ...
            'num': {
                '?': 'A number',
                'str': {
                    '?': ('num', 'A number 2..5'),
                    '_validate': jsh.validate_range(2, 5),
                    None, print_num,
                },
            },
            ...
        }

    Produces the following CLI:

    ::

        > ?
        Possible completions:
          num    Enter a number
        > num ?
        Possible completions:
          num       A number 2..5
        > number foo
        Invalid argument: Value 'foo' is not within range (2, 5)
        > num 10
        Invalid argument: Value 10 is not within range (2, 5)
        > num 3
        User entered 3

.. attribute:: validate_in(iter)

    Validates that the provided string is one of a given list. Takes an iterable
    of strings, and validates that the user entered string is one of them.

    .. code-block:: python

        import jsh

        def print_data(cli, data):
            print 'User entered {}'.format(data)

        layout = {
            ...
            'foo': {
                '?': 'Something',
                'str': {
                    '?': ('data', 'Something'),
                    '_validate': jsh.validate(['one', 'two', 'three']),
                    None, print_data,
                },
            },
            ...
        }

    Produces the following CLI:

    ::

        > ?
        Possible completions:
          foo       Something
        > foo ?
        Possible completions:
          data      Something
        > foo four
        Invalid argument: 'four' is not valid. Choices are: one, two, three
        > num one
        User entered one

