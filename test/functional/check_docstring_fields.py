"""Module docstring  # [malformed-docstring-field, malformed-docstring-field, missing-docstring-field]

blablabla
blablablabla

:version:1.2.3
:date:

some additional information
"""

def func(foo, bar):  # [missing-param-doc, missing-type-doc]
    """docstring
    """
    return foo, bar

class MyClass(object):  # [missing-type-doc]
    """
    MyClass docstring (should describe __init__ params)

    :param int par1: some param
    :param par2: some other param
    """
    def __init__(self, par1, par2):
        self.par1 = par1
        self.par2 = par2

    def method(self, par3, par4):  # [missing-param-doc, missing-type-doc, missing-docstring-description]
        """

        :param int par1: some param
        :param bool par4: some param
        """
        return par3, par4
