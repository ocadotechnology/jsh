CLI Options
===========

The following options are available as arguments to the ``jsh.JSH`` object to customise
the CLI for your usage.

.. attribute:: prompt

    Default: ``'> '``

    A string containing the prompt to display before every command. If using sections,
    the use of ``{section}`` within the string will be replaced with the section
    the user is currently inside.

.. attribute:: section_delims

    Default: ``('(', ')')``

    A tuple of two strings to wrap around the section name when sections are used
    and the prompt contains ``{section}``.

.. attribute:: ignore_case

    Default: ``False``

    A boolean to control whether or not the CLI is case-sensitive when completing
    commands.

.. attribute:: complete_on_space

    Default: ``True``

    A boolean to control whether or not a partially-entered command is completed
    when the user presses space.
