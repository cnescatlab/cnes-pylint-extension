"""Checks the access to sys.argv triggers a refactor message
"""
#pylint: disable=too-few-comments,missing-docstring-field

import sys as s
import sys
from sys import argv as a

def function1():
    a = s.argv[0]  # [sys-argv-used]

print a  # [sys-argv-used]

if len(sys.argv > 1):  # [sys-argv-used]
    param = sys.argv[1]  # [sys-argv-used]

stdout = sys.stdout
