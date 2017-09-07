"""Checks the use of sys.exit() out of the __main__ scope triggers a refactor
message
"""
#pylint: disable=too-few-comments,missing-docstring-field

import sys as s
import sys
from sys import exit as e

def main():
    """Calling sys.exit() from here is not a good practice"""
    if True:
        e(4)  # [sys-exit-used]
    else:
        sys.exit(5)  # [sys-exit-used]

e(6)  # [sys-exit-used]
toto.exit(10)
exit(11)

if True:
    sys.exit(7)  # [sys-exit-used]

if __name__ == '__something__':
    s.exit(8)  # [sys-exit-used]

if __name__ == '__main__':
    main()
    sys.exit(1)
