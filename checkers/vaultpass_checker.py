#!/usr/bin/env python3
import argparse
import random
import string
import time

import requests
import socket
import os
import json

from checklib import FlagAdderDown, MumbleService, CorruptedService

flag_adder = 'http://localhost:5000/?team_id={}&round_id={}'
PORT = 7777
RECV_SLEEP = 0.2


def get_flag(team_id, round_id):
    try:
        r = requests.get(flag_adder.format(team_id, round_id))
    except Exception as e:
        raise FlagAdderDown("Flag adder is down " + str(e))
    return r.text


def random_string(n):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(n))


class VaultpassChecker(object):
    def __init__(self, team_url, team_num, round_num, timeout=5):
        self.url = team_url
        self.team_num = team_num
        self.round_num = round_num
        self.timeout = timeout
        os.makedirs('/tmp/vaultpass', exist_ok=True)

    def _data_file(self, round):
        return '/tmp/vaultpass/team_%s_%s.txt' % (self.team_num, round)

    def _login_user(self, user):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        sock.connect((self.url, PORT))
        time.sleep(RECV_SLEEP)
        sock.recv(4096)
        sock.send(('login\n%s\n%s\n' % user).encode('ascii'))
        time.sleep(RECV_SLEEP)
        if not 'Login completed' in sock.recv(4096).decode('ascii'):
            sock.close()
            raise MumbleService("Didn't receive 'Login completed' message")
        return sock

    def _send_request(self, user, another_user, message):
        sock = self._login_user(user)
        sock.send(('send_request\n%s\n%s\n' % (another_user, message)).encode('ascii'))
        time.sleep(RECV_SLEEP)
        sock.recv(4096)
        sock.close()

    def _accept_request(self, user, message):
        sock = self._login_user(user)
        sock.send('list_requests\n'.encode('ascii'))
        time.sleep(RECV_SLEEP)
        requests_data = sock.recv(4096).decode('ascii')
        request_id = None
        try:
            requests = requests_data.split('\n')
            for i in range(1, len(requests), 3):
                if message in requests[i]:
                    request_id = requests[i - 1]
                    request_id = request_id[request_id.find('=') + 1:].strip()
        except Exception:
            raise MumbleService("list_requests returns ill-formated data")
        if request_id is None:
            raise MumbleService("send_requests didn't send the request")
        sock.send(('accept_request\n%s\n' % request_id).encode('ascii'))
        time.sleep(RECV_SLEEP)
        sock.recv(4096)
        sock.close()

    def _create_user(self, data):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        sock.connect((self.url, PORT))
        time.sleep(RECV_SLEEP)
        sock.recv(4096)
        sock.send('register\n'.encode('ascii'))
        time.sleep(RECV_SLEEP)
        reg_data = sock.recv(4096).decode('ascii')
        sock.send(('add_data\n%s\n' % data).encode('ascii'))
        time.sleep(RECV_SLEEP)
        sock.recv(4096)
        sock.close()
        try:
            reg_data = reg_data.split('\n')
            login = reg_data[2]
            login = login[login.find('=') + 1:].strip()
            auth = reg_data[3]
            auth = auth[auth.find('=') + 1:].strip()
            return (login, auth)
        except Exception:
            raise MumbleService('Failed to register and retrieve auth token')

    def _get_data(self, user, data_user):
        sock = self._login_user(user)
        sock.send((('get_data\n%s\n') % data_user).encode('ascii'))
        time.sleep(RECV_SLEEP)
        text = sock.recv(4096).decode('ascii').strip()
        sock.close()
        return text

    def _check_prev_round(self):
        with open(self._data_file(self.round_num - 1), 'r') as f:
            for _ in range(0, 3):
                user_id = f.readline().strip()
                auth = f.readline().strip()
                data = f.readline().strip()
                if self._get_data((user_id, auth), user_id) != data:
                    raise CorruptedService('get_data check failed')

    def run(self):
        if os.path.exists(self._data_file(self.round_num - 1)):
            self._check_prev_round()
        data_1 = random_string(64)
        data_2 = get_flag(self.team_num, self.round_num)
        data_3 = get_flag(self.team_num, self.round_num)
        user_1 = self._create_user(data_1)
        user_2 = self._create_user(data_2)
        user_3 = self._create_user(data_3)
        request_message = random_string(64)
        self._send_request(user_2, user_3[0], request_message)
        self._accept_request(user_3, request_message)

        if self._get_data(user_1, user_1[0]) != data_1:
            raise MumbleService('add_data check failed')
        if self._get_data(user_2, user_2[0]) != data_2:
            raise MumbleService('add_data check failed')
        if self._get_data(user_3, user_3[0]) != data_3:
            raise MumbleService('add_data check failed')
        if self._get_data(user_1, user_3[0]) != 'Permissions denied':
            raise MumbleService('get_data permission check failed')
        if self._get_data(user_2, user_3[0]) != data_3:
            raise MumbleService('get_data permission check failed')
        with open(self._data_file(self.round_num), 'w') as f:
            f.write(user_1[0] + '\n')
            f.write(user_1[1] + '\n')
            f.write(data_1 + '\n')
            f.write(user_2[0] + '\n')
            f.write(user_2[1] + '\n')
            f.write(data_2 + '\n')
            f.write(user_3[0] + '\n')
            f.write(user_3[1] + '\n')
            f.write(data_3 + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Vaulpass checker')
    parser.add_argument('-t', '--team_id', action='store', dest='team_id', help='ID of team what be checked', type=str,
                        required=True)
    parser.add_argument('-r', '--round_id', action='store', dest='round_id', help='ID of current round', type=int,
                        required=True)
    parser.add_argument('-ip', '--ip', action='store', dest='team_ip', help='IP if team', type=str, required=True)

    parser.add_argument('-tl', '--time_limit', action='store', dest='time_limit', help='time limit for socket request',
                        type=int)
    arguments = parser.parse_args()
    round_id = arguments.round_id
    team_id = arguments.team_id
    time_out = getattr(arguments, 'time_limit', 5)
    team_url = arguments.team_ip
    checker = VaultpassChecker(team_url, team_id, round_id, time_out)

    status = ""
    status_message = ""
    try:
        checker.run()
    except MumbleService as e:
        status = "Mumble"
        status_message = str(e)
    except CorruptedService as e:
        status = "Corrupted"
        status_message = str(e)
    except FlagAdderDown as e:
        status = "Our fault :("
        status_message = str(e)
    except socket.timeout as e:
        status = "Down"
        status_message = ""
    except Exception as e:
        status = "Down"
        status_message = ""
    else:
        if status == "":
            status = "Up"
    print(json.dumps({'team_id': int(team_id), 'status_message': status_message, 'status': status}))
