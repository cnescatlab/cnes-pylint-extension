"""Checks there is no more than one exit statement per loop"""
#pylint: disable=too-few-comments,too-high-complexity,too-high-complexity-simplified,missing-docstring-field

def func():
    for i in range(10):  # [multiple-exit-statements]
        if i > 3:
            break
        if i > 5:
            return

    while True:
        if False:
            break

    for i in range(10):
        return

    for i in range(10):  # [multiple-exit-statements]
        if i > 3:
            break
        while True:
            break
        j = i*2
        if True:
            if j > 6:
                break

for var in range(10):
    var += 2
    if var > 6:
        break
    var2 = 0
    while var2 < var:
        var += 1
        if var2 > 2:
            break
