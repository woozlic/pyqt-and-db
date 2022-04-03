import os.path
import signal
import subprocess
import time
import sys

PYTHON_PATH = sys.executable
BASE_PATH = os.path.dirname(__file__)


def get_subprocess(file_with_args):
    time.sleep(0.2)
    cmd = f'{PYTHON_PATH} {BASE_PATH}/{file_with_args}'
    return subprocess.Popen(['gnome-terminal', "--disable-factory", "--", "bash", "-c", cmd], preexec_fn=os.setpgrp)


processes = []

if __name__ == '__main__':
    while True:
        prompt = input('Type: x - kill all processes, s - create server and 2 clients, q - quit: ')
        if prompt == 's':
            server = get_subprocess('server.py')
            processes.append(server)
            for i in range(2):
                processes.append(get_subprocess(f'client.py -n user_{i}'))
        elif prompt == 'x':
            while processes:
                victim = processes.pop()
                os.killpg(os.getpgid(victim.pid), signal.SIGTERM)
        else:
            break
