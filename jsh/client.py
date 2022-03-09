
import readline
import shlex
import six
import sys

from .exceptions import JSHError


class JSH(object):
    section = None

    def __init__(
        self,
        layout,
        prompt='> ',
        section_delims=('(', ')'),
        ignore_case=False,
        complete_on_space=True
    ):
        self.layout = layout
        self.prompt = prompt
        self.section_delims = section_delims
        self.ignore_case = ignore_case

        readline.parse_and_bind('set bell-style none')
        readline.parse_and_bind('tab: complete')
        readline.parse_and_bind('"?": "\\C-v?\\t\\d"')
        if complete_on_space:
            readline.parse_and_bind('" ": "\\t"')
            readline.parse_and_bind('"\\r": "\\C-v\\n\\t\\d\\n"')
        readline.set_completer_delims(' ')
        readline.set_completer(self.completer)

    def get_prompt(self):
        return self.prompt.format(section='{0}{1}{2}'.format(
            self.section_delims[0],
            self.section,
            self.section_delims[1]
        ) if self.section else '')

    def read_and_execute(self):
        command = self.get_input()
        if command:
            return self.run_command(command)

    def get_input(self):
        try:
            command = six.moves.input(self.get_prompt()).strip()
        except EOFError:
            print()
            raise
        except KeyboardInterrupt:
            print()
            return None
        return command

    def redraw_prompt(self):
        print(self.get_prompt().strip(), readline.get_line_buffer().rstrip('?'), end=' ', flush=True)

    def commands(self):
        def walk(level, path=None, paths=None):
            if path is None:
                path = []
            if paths is None:
                paths = []
            new_paths = []
            if type(level) == dict:
                for key in list(level.keys()):
                    if key in ['\t', '?']:
                        continue
                    if key is None or len(path) == 1 and key == self.section:
                        new_path = path
                    elif key == str and '?' in level[str]:
                        compl = level[str]['?']
                        new_path = path + ['<{0}>'.format(compl if type(compl) == str else compl[0])]
                    elif key == str:
                        new_path = path + ['<...>']
                    else:
                        new_path = path + [key]
                    new_paths.extend(walk(level[key], new_path, paths))
            else:
                new_paths.append(path)
            return paths + new_paths
        return sorted(walk(self.layout))

    @property
    def completer(self):
        def complete(text, state):

            # Allowing bare except: clauses because errors inside the completer just get hidden
            # pylint: disable=W0702

            stext = text.rstrip('?\n')

            try:
                parts = shlex.split(readline.get_line_buffer().rstrip('?')[:readline.get_endidx()].lower())
            except:
                # Inside quotes, don't do any fancy completion
                if state == 0:
                    return text + ' '
                else:
                    return None

            # ? entered by itself, signify with None
            if not stext:
                parts.append(None)
            else:
                parts.pop()

            depth = 0
            completions = {}
            hidden_completions = set()
            args = []
            level = self.layout
            while True:

                # Leaf node, no more completions
                if hasattr(level, '__call__'):
                    break

                # User-defined list of completions {'\t': some_func}
                elif type(level) == dict and '\t' in level and str in level and (not parts or parts[0] is None):

                    try:
                        possibilities = level['\t'](self, *args)
                        if isinstance(possibilities, dict):
                            dynamic = possibilities
                        else:
                            dynamic = dict((comp, '') for comp in possibilities)
                    except:
                        dynamic = {}
                    completions.update(dynamic)
                    completions.update(dict((key, level[key].get('?', '') if type(level[key]) == dict else '') for key in list(level.keys())))
                    break

                # Walk down the levels
                elif (type(level) == dict and
                        (parts and parts[0] is not None and
                         (parts[0] in level or str in level) or
                         depth == 1 and self.section is not None and
                         self.section in level)):

                    if parts and parts[0] in level:
                        level = level[parts[0]]
                        parts.pop(0)
                    elif depth == 1 and self.section is not None and self.section in level:
                        level = level[self.section]
                    elif parts and parts[0] is not None and str in level:
                        level = level[str]
                        args.append(parts.pop(0))
                    depth += 1

                # We have a dict at this level, get this section's completions
                elif type(level) == dict:

                    completions = {}
                    hidden_completions = set()
                    for key, value in list(level.items()):
                        help_text = ''
                        if isinstance(key, six.string_types) and key.startswith('_'):
                            continue
                        if isinstance(value, dict):
                            if value.get('_hidden', False):
                                hidden_completions.add(key)
                            help_text = value.get('?', '')
                        completions[key] = help_text
                    break

                # If we reach here, there are no valid completions at this level
                else:
                    break

            # If you've typed a valid option followed by <tab> or <space>, limit completions to just that option
            if stext in completions and not text.endswith('?'):
                completions = {stext: completions[stext]}
                if stext in hidden_completions:
                    hidden_completions.remove(stext)
            # Otherwise, limit completions to ones that start with what you've typed
            else:
                completions = dict((key, value) for key, value in six.iteritems(completions) if key not in (None, str, '\t', '?') and key.startswith(stext))

            # If the user has pressed enter, but there's not just one way to complete the command (0 or 2+), leave it as it is
            if text == '\n' or text.endswith('\n') and len(completions) != 1:
                return None

            # If the user has requested help, display the available options
            elif text.endswith('?'):

                print()
                # If a variable is available, add it's <name> to completions
                if not hasattr(level, '__call__') and str in level and type(level[str]) == dict and '?' in level[str] and '\t' not in level[str]:
                    compl = level[str]['?']
                    if isinstance(compl, six.string_types):
                        completions['<{0}>'.format(compl)] = level.get('?', '')
                    else:
                        completions['<{0}>'.format(compl[0])] = compl[1]

                # End of a valid command
                if (hasattr(level, '__call__') or None in level) and len(text) == 1:
                    completions['<[Enter]>'] = 'Execute this command'

                # Display valid completions
                if completions:
                    just = max(list(map(len, list(completions.keys()))))
                    print('Possible completions:')

                    def comp_func(comp):
                        if comp.startswith('<['):
                            return '!!'
                        elif comp.startswith('<'):
                            return '!' + comp
                        return comp

                    for key in sorted([k for k in list(completions.keys()) if k not in hidden_completions], key=comp_func):
                        print('  {0}   {1}'.format(key.ljust(just), completions[key]))

                else:
                    print('No valid completions')
                self.redraw_prompt()
                return None

            # Normalise completion dictionary to format required by readline
            else:

                if (str in level and '\t' not in level and
                        not any(key.startswith(stext) for key in set(level.keys()) - set([str, '?', None])) and
                        stext.rstrip(' ')):

                    if '_validate' in level[str]:
                        validation = level[str]['_validate'](self, stext)
                        if validation is not True:
                            print()
                            print('Invalid argument: {}'.format(validation))
                            self.redraw_prompt()
                            return None
                    completions[stext] = ''

                if text.endswith('\n') and len(completions) != 1:
                    return None

                comp_strings = [completion + ' ' for completion in set(completions.keys()) if completion not in hidden_completions]
                if len(comp_strings) > state:
                    return sorted(comp_strings)[state]
                else:
                    return None

        return complete

    def run_command(self, command):
        try:
            parts = shlex.split(command.lower() if self.ignore_case else command)
        except ValueError as err:
            raise JSHError('Parse error: {0}'.format(err.message.lower()))
        parts.append(None)

        args = []
        kwargs = {}
        consumed = []
        depth = 0
        level = self.layout
        while True:

            # Leaf node, this is the command we actually want to call
            if hasattr(level, '__call__'):
                if parts and parts[-1] is None:
                    parts.pop()
                # If we've reached this level and there are still arguments left to process, they're unexpected
                if parts:
                    raise JSHError("Unexpected arguments{0}: '{1}'".format(
                        " after '{0}'".format(' '.join(consumed)) if consumed else '',
                        ' '.join(parts)
                    ))
                return level(self, *args, **kwargs)

            # Walk down the levels, matching the next arguments in the command
            elif (type(level) == dict and
                    (parts and parts[0] in level or
                    parts and parts[0] is not None and str in level or
                    depth == 1 and self.section is not None and self.section in level)):

                # The next argument is a command name, descend
                if parts and parts[0] in level:
                    level = level[parts[0]]
                    consumed.append(parts.pop(0))
                # If we're in a section, descend without consuming a command
                elif depth == 1 and self.section is not None and self.section in level:
                    level = level[self.section]
                # The next argument is a str value, add it to args/kwargs for the final command call and descend
                elif parts and parts[0] is not None and str in level:
                    level = level[str]
                    if '_validate' in level:
                        validation = level['_validate'](self, parts[0])
                        if validation is not True:
                            print('Invalid argument: {}'.format(validation))
                            return
                    kwarg = level.get('_kwarg', False)
                    if kwarg:
                        kwargs[consumed[-1] if kwarg is True else kwarg] = parts[0]
                    else:
                        args.append(parts[0])
                    consumed.append(parts.pop(0))
                depth += 1

            else:
                if parts and parts[-1] is None:
                    parts.pop()
                if parts:
                    raise JSHError("Parse error at '{0}'{1}".format(
                        ' '.join(parts),
                        " after '{0}'".format(' '.join(consumed)) if consumed else '',
                    ))
                else:
                    raise JSHError("Incomplete command '{0}'".format(' '.join(consumed)))


# pylint: disable=W0622
def exit(whatever):
    if type(whatever) == JSH:
        sys.exit(0)
    else:
        # pylint: disable=W0622
        def quit(_):
            sys.exit(whatever)
        return quit


def show_commands(cli):
    print('Available commands:')
    for command in cli.commands():
        print('  {0}'.format(' '.join(command)))


def set_section(section):
    def set_section(cli):
        cli.section = section
    return set_section


def validate_int(_, value):
    try:
        int(value)
    except ValueError:
        return '{0!r} is not a valid integer.'.format(value)
    return True


def validate_in(options):
    def inner(_, value):
        if value in options:
            return True
        return '{0!r} is not valid. Choices are: {1}'.format(value, ', '.join(str(x) for x in options))
    return inner


def validate_range(min_val, max_val):
    def inner(_, value):
        message = 'Value {0!r} is not within range ({1}, {2})'.format(value, min_val, max_val)
        try:
            val = int(value)
        except ValueError:
            return message
        if val < min_val or val > max_val:
            return message
        return True
    return inner


def run(layout):
    cli = JSH(layout)
    while True:
        try:
            cli.read_and_execute()
        except JSHError as err:
            print(err)
        except EOFError:
            break
