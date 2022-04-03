from ipaddress import ip_address, IPv4Address, IPv6Address
import subprocess
import threading
import platform
import time
from tabulate import tabulate


def check_ip_available(ip_reachable: list[list[str]]):
    """
    Checks if IP is available.
    :param ip_reachable: IP address and his reachability. Ex.: [IPv4Address('132.0.0.1'), False]
    :return: True if available, False if not.
    """
    try:
        ip = ip_address(ip_reachable[0])
    except ValueError:
        ip = ip_reachable[0]
    try:
        subprocess.check_output("ping -{} 1 {}".format('n' if platform.system().lower() == "windows" else 'c',
                                                       ip), shell=True)
    except subprocess.CalledProcessError:
        ip_reachable[1] = False
    else:
        ip_reachable[1] = True


def host_ping(ip_list: list[str], to_print: bool = True):
    """
    Iterate through given IP list and checks his availability.
    :param ip_list: list of IPs
    :param to_print: True if results should be printed. False if results should be returned.
    :return: None
    """
    threads = []
    ip_list = [[ip, None] for ip in ip_list]
    ip_hash_table = {
        True: 'Узел %s доступен',
        False: 'Узел %s не доступен',
    }
    for ip in ip_list:
        check = threading.Thread(target=check_ip_available, args=(ip, ))
        check.daemon = True
        check.start()
        threads.append(check)
    while True:
        if any([t.is_alive() for t in threads]):
            continue
        break
    if to_print:
        for ip, reachability in ip_list:
            print(ip_hash_table[reachability] % ip)
        print(f'Host ping executed in {time.time() - t1} s.')
    else:
        return ip_list


def host_range_ping(to_print: bool = True):
    """
    Creates a range of ip addresses in given range (only last octet is changing) and checks their reachability.
    :param to_print: True if results should be printed. False if results should be returned.
    :return:
    """
    ip = input('Enter IP address: ')
    ip = ip_address(ip)
    while True:
        ip_range = int(input('Enter IP range: '))
        last_octet = int(str(ip).split('.')[-1])
        if last_octet + ip_range > 256:
            print('Only last octet is changing (0 - 256), so please input correct IP range.')
            continue
        break
    ip_list = [ip+i for i in range(ip_range)]
    ip_list = host_ping(ip_list, to_print=to_print)
    return ip_list


def host_range_ping_tab() -> None:
    """
    Creates a range of ip addresses in given range (only last octet is changing).
    Prints a range of IP addresses and their reachability as a table.
    :return:
    """
    ip_list = host_range_ping(to_print=False)
    ip_dict = {'Reachable': [], 'Unreachable': []}
    for ip, reachability in ip_list:
        if reachability:
            ip_dict['Reachable'].append(ip)
        else:
            ip_dict['Unreachable'].append(ip)
    print()
    print(tabulate(ip_dict, headers='keys'))


if __name__ == '__main__':
    t1 = time.time()
    host_ping(['yandex.ru', 'google.com', 'blalsfkamsk.fkasfa'])
    print()
    host_range_ping()
    host_range_ping_tab()

