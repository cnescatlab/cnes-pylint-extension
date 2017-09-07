"""Checks the access to environment variables triggers a refactor message
"""
#pylint: disable=too-few-comments,missing-docstring-field

import os as o
import os
from os import environ as e

def function1():
    a = os.environ  # [os-environ-used]

print e  # [os-environ-used]
env = o.getenv()  # [os-environ-used]
o.putenv('TOTO', 'titi')  # [os-environ-used]
sep = o.sep
o.unsetenv('TOTO')  # [os-environ-used]
