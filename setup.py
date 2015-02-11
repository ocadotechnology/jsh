"""Setup for JSH"""

from setuptools import setup
from platform import system
from jsh.version import __VERSION__

setup(
	name			= 'jsh',
	version			= __VERSION__,
	description		= 'JunOS-like shell library for Python',
	author			= 'InfDev',
	author_email		= 'infdev@ocado.com',
	packages		= [ 'jsh' ],
	install_requires	= [ 'readline' ] if system() == 'Darwin' else []
)

