"""Check that is a file is opened without using a context manager, a refactor
message is triggered. Same thing for threading locks.
"""
# pylint: disable=too-few-comments,missing-docstring-field
import threading

with open('afile.txt') as af:
    pass

f = open('afile.txt')  # [use-context-manager]

lock = threading.RLock()
with lock:
    do_something()
lock.acquire()  # [use-context-manager]
lock.release()

lock = threading.Lock()
lock.acquire()  # [use-context-manager]

lock = threading.Semaphore()
lock.acquire()  # [use-context-manager]
