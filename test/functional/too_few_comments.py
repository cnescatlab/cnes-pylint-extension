"""Docstring introduction  # [too-few-comments]

This test checks unsufficient comment lines in a function or a module triggers
a refactor message
"""
#pylint: disable=too-high-complexity,missing-docstring-field

def function():
    """docstring"""
    var = 2

    # loop
    while True:
        # some more comment
        # bla bla

        if False:
            pass
        else:
            var += 1

    # end of the function

# global code
for i in range(10):
    if i == 0:
        pass
    elif i == 1:
        pass
    if i == 2:
        pass
    elif i == 3:
        pass
    elif i == 4:
        pass
    elif i == 5:
        pass
    elif i == 6:
        pass
    elif i == 7:
        pass
    elif i == 8:
        pass
    elif i == 9:
        pass
    elif i == 10:
        pass

def function2():  # [too-few-comments]
    """description

    params
    """
    # comment
    var = True
    if var:
        pass
    elif var:
        pass
    elif var:
        pass
    elif var:
        pass
    elif var:
        pass
    elif var:
        pass
    elif var:
        pass
    var = True
    var = True

def short_func():
    var = 2
    for i in range(var):
        while True:
            var += i
            if var > 10:
                break
            else:
                pass

