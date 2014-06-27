#!/usr/bin/env python

import readline
import shlex
import sys

class JSHError(Exception):
	pass

class JSH(object):
	section = None
	def __init__(self, layout, prompt='> ', section_delims=('(', ')'), ignore_case=False):
		self.layout = layout
		self.prompt = prompt
		self.section_delims = section_delims
		self.ignore_case = ignore_case
		readline.parse_and_bind('tab: complete')
		readline.parse_and_bind('"?": "\\C-v?\\t\\d"')
		readline.parse_and_bind('" ": "\\t"')
		readline.parse_and_bind('"\\r": "\\C-v\\n\\t\\d\\n"')
		readline.set_completer_delims(' ')
		readline.set_completer(self.completer)
	def get_prompt(self):
		return self.prompt.format(section='{0}{1}{2}'.format(self.section_delims[0], self.section, self.section_delims[1]) if self.section else '')
	def read_and_execute(self):
		command = self.get_input()
		if command:
			return self.run_command(command)
	def get_input(self):
		try:
			command = raw_input(self.get_prompt()).strip()
		except EOFError:
			print
			raise
		except KeyboardInterrupt:
			print
			return None
		return command 
	def commands(self):
		def walk(level, path=[], paths=[]):
			new_paths = []
			if type(level) == dict:
				for key in level.keys():
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
			stext = text.rstrip('?\n')

			try:
				parts = shlex.split(readline.get_line_buffer().rstrip('?')[:readline.get_endidx()].lower())
			except:
				if state == 0:
					return text + ' '
				else:
					return None

			if not stext:
				parts.append(None)
			else:
				parts.pop()

			depth = 0
			completions = {}
			args = []
			level = self.layout
			while True:
				if hasattr(level, '__call__'):
					break
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
					completions.update(dict((key, level[key].get('?', '') if type(level[key]) == dict else '') for key in level.keys()))
					break
				elif type(level) == dict and (parts and parts[0] is not None and (parts[0] in level or str in level) or depth == 1 and self.section is not None and self.section in level):
					if parts and parts[0] in level:
						level = level[parts[0]]
						parts.pop(0)
					elif depth == 1 and self.section is not None and self.section in level:
						level = level[self.section]
					elif parts and parts[0] is not None and str in level:
						level = level[str]
						args.append(parts.pop(0))
					depth += 1
				elif type(level) == dict:
					completions = dict((key, level[key].get('?', '') if type(level[key]) == dict else '') for key in level.keys())
					break
				else:
					break

			if stext in completions:
				completions = {stext: completions[stext]}
			else:
				completions = dict((key, value) for key, value in completions.iteritems() if key not in [None, str, '\t', '?'] and key.startswith(stext))

			if text == '\n' or text.endswith('\n') and (len(completions) > 1 or str in level):
				return None
			elif text.endswith('?'):
				print
				if str in level and type(level[str]) == dict and '?' in level[str] and '\t' not in level[str]:
					compl = level[str]['?']
					if type(compl) == str:
						completions['<{0}>'.format(compl)] = ''
					else:
						completions['<{0}>'.format(compl[0])] = compl[1]
				if None in level:
					completions['<[Enter]>'] = 'Execute this command'
				if completions:
					just = max(map(len, completions.keys()))
					print 'Possible completions:'
					for key in sorted(completions.keys(), key=lambda comp: '!!' if comp.startswith('<[') else ('!' + comp if comp.startswith('<') else comp)):
						print '  {0}   {1}'.format(key.ljust(just), completions[key])
				else:
					print 'No valid completions'
				print '{0}{1}'.format(self.get_prompt(), readline.get_line_buffer()),
				return None
			else:
				if str in level and '\t' not in level:
					completions[text] = ''
				comp_strings = [completion + ' ' for completion in set(completions.keys())]
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
		consumed = []
		depth = 0
		level = self.layout
		while True:
			if hasattr(level, '__call__'):
				if parts and parts[-1] is None:
					parts.pop()
				if parts:
					raise JSHError("Unexpected arguments{0}: '{1}'".format(
						" after '{0}'".format(' '.join(consumed)) if consumed else '',
						' '.join(parts)
					))
				return level(self, *args)
			elif type(level) == dict and (parts and parts[0] in level or parts and parts[0] is not None and str in level or depth == 1 and self.section is not None and self.section in level):
				if parts and parts[0] in level:
					level = level[parts[0]]
					consumed.append(parts.pop(0))
				elif depth == 1 and self.section is not None and self.section in level:
					level = level[self.section]
				elif parts and parts[0] is not None and str in level:
					args.append(parts[0])
					level = level[str]
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

def exit(whatever):
	if type(whatever) == JSH:
		sys.exit(0)
	else:
		def quit(cli):
			sys.exit(whatever)
		return quit

def show_commands(cli):
	print 'Available commands:'
	for command in cli.commands():
		print '  {0}'.format(' '.join(command))

def set_section(section):
	def set_section(cli):
		cli.section = section
	return set_section

