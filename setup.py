"""Setup for JSH"""

from distutils.core import setup
from gitversion import get_git_version

setup(
	name = 'jsh',
	version = get_git_version(__file__),
	description = 'JunOS-like shell',
	author = 'InfDev',
	author_email = 'infdev@ocado.com',
	py_modules = ['jsh']
)

