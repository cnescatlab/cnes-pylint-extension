"""Check no method nor attribute it named after a builtin"""
#pylint: disable=too-few-comments,missing-docstring-field

class MyClass(object):
    def __init__(self):
        ((self.file, (self.str, self.something)), plop) = (('test.txt', 'hello'), 'plop')  # [builtin-name-used, builtin-name-used]

    bool = True  # [builtin-name-used]

    def map(self):  # [builtin-name-used]
        pass

    def dummy_method(cls):
        pass
    zip = classmethod(dummy_method)  # [builtin-name-used]

MyClass.dict = "hi there"  # [builtin-name-used]


class ChildClass(MyClass):

    def map(self):
        """inherited: should be ok"""
