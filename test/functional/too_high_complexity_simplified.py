"""Checks functions and methods having a high McCabe number trigger a refactor
message
"""
#pylint: disable=too-few-comments,multiple-exit-statements,too-high-complexity
#pylint: disable=recursive-call, missing-docstring-field

def func():  # [too-high-complexity-simplified]
    '''
    docstring
    '''
    if True:
        while True:
            for i in range(10):
                if i == 1:
                    break
                elif i == 2:
                    break
                elif i == 5:
                    break
                else:
                    break
    else:
        try:
            while True:
                pass
        except Exception1:
            pass
        except Exception2:
            pass
    if True:
        a = 2
        func()
    else:
        return


class MyClass(object):
    def method(self):  # [too-high-complexity-simplified]
        '''
        docstring
        '''
        if True:
            while True:
                for i in range(10):
                    if i == 1:
                        break
                    elif i == 2:
                        break
                    elif i == 5:
                        break
                    else:
                        break
        else:
            try:
                while True:
                    pass
            except Exception1:
                pass
            except Exception2:
                pass
        if True:
            a = 2
            func()
        elif True:
            pass
        else:
            return

def func1():
    """simple function"""
    var = 2
    while True:
        if False:
            pass
        else:
            var += 1
