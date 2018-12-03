#!/usr/bin/env python3
import argparse
import random
import string
import re
import os
import json
import requests
import uuid

from checklib import FlagAdderDown, MumbleService, CheckerSession, CorruptedService

flag_adder = 'http://localhost:5002/?team_id={}&round_id={}'


def new_flag(team_id, round_id):
    try:
        r = requests.get(flag_adder.format(team_id, round_id))
    except Exception as e:
        raise FlagAdderDown("Flag adder is down" + str(e))
    return r.text


def random_string(n):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(n))


class BlackChecker(object):
    def __init__(self, team_url, team_num, round_num, timeout=10):
        self.url = team_url
        self.team_num = team_num
        self.round_num = round_num
        self.time_out = timeout
        self.session = CheckerSession(timeout=self.time_out)
        os.makedirs('/tmp/black', exist_ok=True)

    def register(self):
        login = 'user' + str(uuid.uuid4())
        login = login.replace('-', '')
        login = login[:29]
        data = dict(account=login)

        response = self.session.post(self.url + '/register', data=data)
        if response.status_code != 200 or 'ok' not in response.text:
            raise MumbleService("Cant login in service")
        return login

    def place_secret(self, login, text, desc, price=1):
        data = {
            'account': login,
            'secret': text,
            'description': desc,
            'price': price,
        }
        response = self.session.post(self.url + '/place_secret', data=data)
        if response.status_code == 200:
            d = response.json()
            if d['result'][-1] == price:
                return True
        return False

    def get_secret_id(self, login):
        response = self.list_secrets(login)
        if response.status_code == 200:
            j = response.json()
            if len(j['result']) < 0:
                raise MumbleService("Cant see own secrets")
            return j['result'][0]['id']
        raise MumbleService("Cant see own secrets")

    def list_secrets(self, login):
        return self.session.get(self.url + '/my_secrets', params=dict(account=login))

    def get_free_coin(self, login):
        response = self.session.post(self.url + '/free_coin', data=dict(account=login))
        if response.status_code == 200 and response.json()['result'] >= 1:
            return True
        return False

    def buy_secret(self, login, s_id):
        response = self.session.post(self.url + '/buy_secret', data=dict(secret_id=s_id, account=login))
        if response.status_code == 200 and 'ok' in response.text:
            return response.json()['result']['secret']
        raise MumbleService("Cant buy secret")

    def reset_session(self):
        self.session = CheckerSession(timeout=self.time_out)

    def put_flag(self):
        real_user = self.register()
        flag = new_flag(self.team_num, self.round_num)
        descr = random_string(10)
        price = random.randint(13, 50)
        ok = self.place_secret(real_user, flag, descr, price=price)
        if not ok:
            raise MumbleService("Cant create secret")
        return dict(login=real_user, flag=flag)

    def get_flag(self, login, etalon):
        resp = self.list_secrets(login)
        if etalon not in resp.text:
            raise CorruptedService("Cant find own secret")

    def _data_file_name(self):
        return '/tmp/black/check_team_{}_round_{}.txt'.format(self.team_num, self.round_num)

    def _store_data(self, data):
        j_str = json.dumps(data)
        with open(self._data_file_name(), 'w') as out:
            out.write(j_str)

    def _loads_data(self):
        with open(self._data_file_name()) as inp:
            return json.loads(inp.read())

    def run(self):
        # Check round_before
        self.round_num -= 1
        if os.path.exists(self._data_file_name()):
            data = self._loads_data()
            self.get_flag(data['login'], data['flag'])
        self.round_num += 1
        first = self.register()
        not_flag_desc = random_string(10)
        not_flag_secret = random_string(10)
        ok = self.place_secret(first, not_flag_secret, not_flag_desc, price=1)
        if not ok:
            raise MumbleService("Cant create secret")
        s_id = self.get_secret_id(first)

        second = self.register()
        ok = self.get_free_coin(second)
        if not ok:
            raise MumbleService("Cant get free coin")
        secret = self.buy_secret(second, s_id)
        if secret != not_flag_secret:
            raise MumbleService("Cant buy secret")

        d = self.put_flag()
        self._store_data(d)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Service BlackExchange checker')
    parser.add_argument('-t', '--team_id', action='store', dest='team_id', help='ID of team what be checked', type=str,
                        required=True)
    parser.add_argument('-r', '--round_id', action='store', dest='round_id', help='ID of current round', type=int,
                        required=True)
    parser.add_argument('-ip', '--ip', action='store', dest='team_ip', help='IP if team', type=str, required=True)

    parser.add_argument('-tl', '--time_limit', action='store', dest='time_limit', help='time limit for http request',
                        type=int)

    arguments = parser.parse_args()
    round_id = arguments.round_id
    team_id = arguments.team_id
    time_out = getattr(arguments, 'time_limit', 7)
    team_url = "http://" + arguments.team_ip + ":9999"
    checker = BlackChecker(team_url, team_id, round_id, time_out)

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

    except requests.exceptions.RequestException as e:
        status = "Down"
        status_message = ""

    # except Exception as e:
    #     status = "Down"
    #     status_message = str(e)

    else:
        if status == "":
            status = "Up"

    print(json.dumps({'team_id': int(team_id), 'status_message': status_message, 'status': status}))
