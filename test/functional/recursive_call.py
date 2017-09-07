"""Check direct recursion isn't permitted
"""
#pylint: disable=too-few-comments,missing-docstring-field

def func1():
    """does nothing"""

class MyClass(object):
    def func2(self):
        pass

def func2():
    if True:
        func2()  # [recursive-call]
    for i in range(10):
        func1()
    func2()  # [recursive-call]
    c = MyClass()
    c.func2()


