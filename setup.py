"""Setup for JSH"""

from setuptools import setup
from jsh.version import __VERSION__

setup(
	name			= 'jsh',
	version			= __VERSION__,
	description		= 'JunOS-like shell',
	author			= 'InfDev',
	author_email		= 'infdev@ocado.com',
	packages		= [ 'jsh' ],
	install_requires	= [ 'readline' ]
)

