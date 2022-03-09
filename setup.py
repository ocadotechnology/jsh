"""Setup for JSH"""

from setuptools import setup
from setuptools.command.test import test as TestCommand
from platform import system
from jsh.version import __VERSION__


class NoseTestCommand(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # Run nose ensuring that argv simulates running nosetests directly
        import nose
        import os
        os.environ['COVERAGE_PROCESS_START'] = '.coveragerc'
        nose.run_exit(argv=['nosetests'])

INSTALL_REQUIRES = [
    'six',
]

if system() == 'Darwin':
    INSTALL_REQUIRES.append('readline')

setup(
    name='jsh',
    version=__VERSION__,
    description='Junos-like shell library for Python',
    author='Ocado Technology',
    author_email='code@ocado.com',
    long_description=open('README.rst').read(),
    url='https://github.com/ocadotechnology/jsh/',
    packages=['jsh'],
    install_requires=INSTALL_REQUIRES,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    tests_require=[
        'coverage',
        'nose',
        'pexpect < 4.0',
    ],
    cmdclass={'test': NoseTestCommand},
)
