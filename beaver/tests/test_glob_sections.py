# -*- coding: utf-8 -*-
import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

import os
import glob
from beaver.config import BeaverConfig

class ConfigTests(unittest.TestCase):

    def setUp(self):
        self.config = lambda: None
        self.config.config = 'tests/square_bracket_sections.ini'
        self.config.mode = 'bind'
        self.beaver_config = BeaverConfig(self.config)

    def test_globs(self):
        files = [os.path.realpath(x) for x in glob.glob('tests/logs/0x[0-9]*.log')]
        for file in self.beaver_config.getfilepaths():
            self.assertTrue(file in files)

if __name__ == '__main__':
    unittest.main()
