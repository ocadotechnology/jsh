

import os
import pexpect
import unittest

THIS_DIRECTORY = os.path.dirname(__file__)


class TestStringMethods(unittest.TestCase):

    def setUp(self):
        self.child = pexpect.spawnu("python %s/basic_usage" % THIS_DIRECTORY, timeout=1)
        self.child.expect('>')

    def tearDown(self):
        self.child.close()
        try:
            self.child.wait()
        except pexpect.ExceptionPexpect:
            pass

    def test_basic_question(self):
        self.child.send('?')
        self.child.expect('Possible completions:')
        self.child.expect('exit')

    def test_basic_tab(self):
        self.child.send('\t')
        self.child.expect('exit')

    def test_basic_control_d(self):
        self.child.sendcontrol('d')
        self.child.expect(pexpect.EOF)
