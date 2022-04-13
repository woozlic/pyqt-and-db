import os.path
import signal
import subprocess
import time
import sys

platform_name = sys.platform

PYTHON_PATH = sys.executable
BASE_PATH = os.path.dirname(__file__)


def get_subprocess(file, args_list=()):
    time.sleep(0.2)
    if platform_name.startswith('win'):
        cmd = [PYTHON_PATH, BASE_PATH + '\\' + file, *args_list]
        return subprocess.Popen(cmd)
    cmd = f'{PYTHON_PATH} {BASE_PATH}/{file} {" ".join(args_list)}'
    return subprocess.Popen(['gnome-terminal', "--disable-factory", "--", "bash", "-c", cmd], preexec_fn=os.setpgrp)


processes = []

if __name__ == '__main__':
    while True:
        prompt = input('Type: x - kill all processes, s - create server and 2 clients, q - quit: ')
        if prompt == 's':
            server = get_subprocess('server.py')
            processes.append(server)
            for i in range(2):
                processes.append(get_subprocess('client.py', ['-n', f'user_{i}']))
        elif prompt == 'x':
            while processes:
                victim = processes.pop()
                if platform_name.startswith('win'):
                    os.kill(victim.pid, signal.CTRL_C_EVENT)
                else:
                    os.killpg(os.getpgid(victim.pid), signal.SIGTERM)
        else:
            break
