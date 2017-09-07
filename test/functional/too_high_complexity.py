"""Checks functions and methods having a high McCabe number trigger a refactor
message
"""
#pylint: disable=too-few-comments,multiple-exit-statements
#pylint: disable=too-high-complexity-simplified,recursive-call,missing-docstring-field

def func():  # [too-high-complexity]
    '''
    docstring
    '''
    if True:
        a = 2
        func()
    elif True:
        a = 3
    a = 7
    c = 10
    for i in range(10):
        b = 0
        while a > i:
            b += 1
            if b == 1:
                pass
            else:
                a = func2()
                def func4():
                    i = 3
                    for j in range(i):
                        try:
                            pass
                        except Exception1:
                            while True:
                                i += 1
                                if i > 5:
                                    i += 1
                                    break
                                else:
                                    raise Something
                        except Exception2:
                            pass
                        except Exception3:
                            pass
                    return True

class MyClass(object):

    def method1(self):  # [too-high-complexity]
        """complex method"""
        if True:
            a = 2
            func()
        else:
            a = 3
            c = 10
            for i in range(10):
                b = 0
                while a > i:
                    b += 1
                    if b == 5:
                        for j in range(b):
                            try:
                                func1()
                            except Exception1:
                                if a == b:
                                    break
                                else:
                                    pass
                        pass
                    else:
                        a = func2()
                if True:
                    pass
                elif True:
                    pass
                elif True:
                    pass
                elif True:
                    pass
            for i in range(10):
                pass

                var = 2
                while True:
                    if False:
                        pass
                    else:
                        var += 1

def func1():
    """simple function"""
    var = 2
    while True:
        if False:
            pass
        else:
            var += 1
