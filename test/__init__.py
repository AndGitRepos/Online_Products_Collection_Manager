import os, sys

# Get the path to the project root directory
# Allows importing of modules
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root.replace("/test", ""))

import unittest
loader = unittest.TestLoader()
start_dir = 'test'
suite = loader.discover(start_dir)

runner = unittest.TextTestRunner()
runner.run(suite)