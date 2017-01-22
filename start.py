import subprocess
import time    # optionally, might be useful to give the server time to initialize
import sys

args = ['python', '-m', 'bokeh', 'serve', 'main.py']
p = subprocess.Popen(args)

time.sleep(4)
args = ['python', '-m', 'webbrowser', 'http://localhost:5006/main']
p2 = subprocess.Popen(args)

# optional delay for x seconds to give the server time to initialize
pid = p.pid
while 1:
    var = input("Please enter something: ")
    if var == 'stop':
        args = ['kill', '-9', str(pid)]
        p = subprocess.Popen(args)
        sys.exit()


