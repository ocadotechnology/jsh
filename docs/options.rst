Command Options
===============

The following options are available as keys in the layout dictionary.

.. attribute:: '?'

    A string containing a description of what the command at this level does, used
    in the help text output.

.. attribute:: None

    The handler function or method to call when the command at this point is executed
    by pressing Enter. The function is passed at least one argument (the ``JSH``
    instance), and any other arbitrary strings entered by the user previously in
    the command (see ``str`` below).

.. attribute:: '\\t'

    A completion function that should return either a list of available completions
    at this point in the command, or a dictionary of available tab completions and
    their descriptions. The function is passed at least one argument (the ``JSH``
    instance), and any other arbitrary strings entered by the user previously in
    the command (see ``str`` below).

.. attribute:: str

    A level in the layout tree that accepts an arbitrary user string instead of
    a pre-defined command. Like any other level of the tree, the value can either
    be a single function (which will be executed as in the ``None`` key above),
    or a dictionary representing the next level of the tree.

.. attribute:: '_validate'

    A function that is passed the prior token in the command and returns either
    ``True`` (if the token is valid) or a string containing an error message if
    not. Designed to be used under the ``str`` key, this validates the user-defined
    input and will stop the user tab completing an invalid value. JSH provides
    some built-in validators, see :ref:`validators` for more details.

.. attribute:: '_kwarg'

    A string containing the name of a keyword argument, or ``None``. This flag is
    designed to be used under the ``str`` key, and will pass the user-defined input
    as a keyword argument to the final handler function instead of as a plain argument.
    This allows you to decouple the handler function's signature from the layout
    tree. If ``None``, the name of the token prior to the ``str`` token is used
    as the keyword.

.. attribute:: '_hidden'

    Default: ``False``

    A boolean value determining whether this command should be shown in completion
    and help output. Can be used to implement hidden commands that are only available
    if the user knows they are there.
