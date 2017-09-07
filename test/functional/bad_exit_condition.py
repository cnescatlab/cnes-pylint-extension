"""Checks that loop exit conditions don't use equality or difference comparison
"""
#pylint: disable=too-few-comments,missing-docstring-field
string = '   hello world'
i = 0
while string[i] == ' ':  # [bad-exit-condition]
    i += 1
i = 0
while string[i] != 'h':  # [bad-exit-condition]
    i += 1
while i < 5 and string[i] == ' ':  # [bad-exit-condition]
    i += 1
while i > 0:
    i -= 1
while True:
    pass
while string[i] == ' ' and True or i != 3:  # [bad-exit-condition]
    pass
