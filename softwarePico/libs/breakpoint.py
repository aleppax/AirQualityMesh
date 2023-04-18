# breakpoint
import _thread
import sys

def breakpoint():
    unbreak = False
    while not unbreak:
        sys.stdout.flush()
    print('Resuming execution')
    
    
def b():
    _thread.start_new_thread(breakpoint, ())
