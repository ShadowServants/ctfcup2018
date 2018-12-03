#!/usr/bin/env python3
import argparse
import random
import string
import re
import os
import json
import PyPDF2
from io import BytesIO

import requests

from checklib import FlagAdderDown, MumbleService, CheckerSession, CorruptedService

flag_adder = 'http://localhost:5000/?team_id={}&round_id={}'


class CsrfSession(CheckerSession):

    def post(self, url, data=None, json=None, **kwargs):
        if not data:
            data = dict()
        data['csrfmiddlewaretoken'] = self.cookies.get('csrftoken')
        return super().post(url, data, json, **kwargs)


def new_flag(team_id, round_id):
    try:
        r = requests.get(flag_adder.format(team_id, round_id))
    except Exception as e:
        raise FlagAdderDown("Flag adder is down" + str(e))
    return r.text


def random_string(n):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(n))


class ArlingtonChecker(object):
    def __init__(self, team_url, team_num, round_num, timeout=10):
        self.url = team_url
        self.team_num = team_num
        self.round_num = round_num
        self.session = CsrfSession(timeout=timeout)
        self.group_url = None
        self.group_code = None
        self.users_data = []

    def reset_session(self):
        self.session = CsrfSession(timeout=self.session.request_timeout)

    def register(self, add_string=''):
        register_url = self.url + '/auth/register'
        login = 'user{}'.format(random_string(5))
        password = random_string(15)
        data = dict(
            username=login + add_string,
            password=password,
        )
        for i in range(10):
            self.session.get(register_url)
            form_data = dict(data)
            form_data['password2'] = form_data['password']
            form_data['signup_submit'] = 'Enter'
            r = self.session.post(url=register_url, data=form_data, allow_redirects=False)
            if r.status_code == 302:
                return data
            else:
                data['username'] += random_string(2)
        raise MumbleService("Cant register in service")

    def login(self, data):
        login_url = self.url + '/auth/login'
        self.session.get(login_url)
        form_data = dict(data)
        form_data['signup_submit'] = 'Enter'
        r = self.session.post(url=login_url, data=form_data, allow_redirects=False)
        if r.status_code != 302:
            raise MumbleService("Cant login in service")

    def create_draft(self, title, text):
        post_data = dict(title=title, text=text)
        self.session.get(self.url + '/drafts/create')
        response = self.session.post(self.url + '/drafts/create', data=post_data)
        if response.status_code != 200:
            raise MumbleService("Cant create draft")

    def get_drafts_response(self):
        response = self.session.get(self.url + '/drafts/')
        return response

    def visit_main(self):
        self.session.get(self.url + '/')

    @staticmethod
    def get_fake_draft():
        texts = (
            "War... War never changes.The end of the world occurred pretty much as we had predicted.Too many humans, "
            "not enough space or resources to go around. ",
            "Война ... Война никогда не меняется.Конец света произошел в значительной степени, как мы и "
            "предсказывали.Слишком много людей, недостаточно места или ресурсов, чтобы обойти вокруг.",
            "Стіни майстерні були дуже одноманітного, нудного сірого кольору. Та стіна, на яку я саме дивилася, "
            "відрізнялася тим, що була дуже чистого сірого кольору. ПіпБаки були на диво стійкими та надійними, "
            "тому буття техніком з ПіпБаків у Стайні означало довгі періоди бездіяльності. Буття ж учнем техніка з "
            "ПіпБаків означало, що мені діставалася вся буденна робота, доки мій наставник давав хропака у підсобці. "
            "Робота на кшталт чистки стін.",
            "Оторвав всё, что можно было оторвать от робота-паука, я взвесила доступные варианты. Я не могла "
            "оставаться тут вечно. Если я буду двигаться очень быстро, я успею пробежать по дорожке, и роботы внизу в "
            "меня не попадут. Их оружие казалось мне не слишком точным. Но первые несколько метров мостика теперь "
            "болтались в воздухе и угрожающе прогнулись. И чем дольше я на него смотрела, тем меньше мне хотелось "
            "оказаться на нём.",
            "Arlington Library is easily found by following the Potomac River south past the Citadel, then turning "
            "west to follow the road just south. It is directly across from Alexandria Arms and about two miles "
            "west-southwest of the Jefferson Memorial. ",

        )
        return random.choice(texts)

    @staticmethod
    def get_fake_document():
        docs = {'Railgun': '1.Findrails',
                'Circle': 'TheLength',
                'Nuclear': '(a)Drugs',
                }
        k = random.choice(list(docs.keys()))
        d = docs[k]
        file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'arlinton_data', k.lower() + '.txt'))
        document_data = dict(title=k, etalon=d)
        with open(file_path, 'r') as f:
            data = f.read()
        document_data['text'] = data
        return document_data

    def create_group(self):
        group_name = "Brotherhood Of " + random_string(5)
        self.session.get(self.url + '/groups/create')
        for i in range(10):
            resp = self.session.post(self.url + '/groups/create', data=dict(name=group_name))
            if len(resp.history) > 0:
                return resp.url
        raise MumbleService("Cant create group")

    def get_group_invite_code(self, group_url):
        resp = self.session.get(group_url, allow_redirects=False)
        if resp.status_code != 200:
            raise MumbleService("Cant get group page")
        response_text = resp.text
        res = re.findall(r'Invite code: [A-Za-z0-9_+-\/]+', response_text)
        if len(res) != 1:
            raise MumbleService("Cant find invite code. Or found many")
        code = res[0].split()[-1].strip()
        return code

    def create_document(self, title, text):
        document_urls = self.group_url + 'documents/create'
        post_data = dict(title=title, text=text)
        self.session.get(document_urls)
        response = self.session.post(document_urls, data=post_data)
        if response.status_code != 200 or title not in response.text:
            raise MumbleService("Cant create document")

    def search_documents(self, query):
        return self.session.get(self.group_url + 'documents/search', params=dict(q=query))

    def join_group(self, code):
        join_url = self.url + '/groups/join/' + code + '/'
        resp = self.session.get(join_url, allow_redirects=False)
        if not resp.is_redirect:
            raise MumbleService("Cant join group by code")

    def find_last_render(self, user_num=-1):
        document_url = self.group_url + 'documents/list'
        resp = self.session.get(document_url)
        if resp.status_code != 200:
            raise MumbleService("Cant get documents page")
        docs = re.findall(r'\/rendered_docs\/[A-Za-z0-9_+-\/]+\.pdf', resp.text)
        if len(docs) < 2:
            raise CorruptedService("Renders not found")
        return docs[user_num]

    def check_render(self, render_url, etalon_pattern):
        resp = self.session.get(self.url + render_url, stream=True)
        b_io = BytesIO(resp.raw.read())
        reader = PyPDF2.PdfFileReader(b_io)
        page = reader.getPage(0)
        text = page.extractText()
        if etalon_pattern not in text:
            raise CorruptedService("Cant find flag in render")

    def put_first(self):
        check_data = dict()
        first_user_data = self.register()
        self.login(first_user_data)
        check_data['auth'] = first_user_data
        flag = new_flag(self.team_num, self.round_num)
        self.create_draft('Secret', flag)
        check_data['draft'] = flag
        self.group_url = self.create_group()
        self.group_code = self.get_group_invite_code(self.group_url)
        check_data['group_url'] = self.group_url
        document_data = self.get_fake_document()
        self.create_document(document_data['title'], document_data['text'])
        check_data['document'] = document_data
        self.users_data.append(check_data)

    def put_second(self):
        check_data = dict()
        user_data = self.register()
        self.login(user_data)
        check_data['auth'] = user_data
        text = self.get_fake_draft()
        self.create_draft('New', text)
        check_data['draft'] = text
        self.join_group(self.group_code)
        check_data['group_url'] = self.group_url
        flag = new_flag(self.team_num, self.round_num)
        document_data = {'title': 'Secret', 'text': flag, 'etalon': flag}
        self.create_document(document_data['title'], document_data['text'])
        check_data['document'] = document_data
        self.users_data.append(check_data)

    def check_user(self, user_data, user_num=-1):
        self.login(user_data.get('auth', {}))
        resp = self.get_drafts_response()
        if resp.status_code != 200 or user_data['draft'].strip() not in resp.text:
            raise CorruptedService("Cant get draft")
        document_data = user_data['document']
        # Should we check fake flag ???
        # if document_data['title'] == 'Secret':
        self.group_url = user_data['group_url']
        flag = document_data['text']
        resp = self.search_documents(document_data['title'])
        if resp.status_code != 200 or flag not in resp.text:
            raise CorruptedService("Cant find document")
        renderer_url = self.find_last_render(user_num)
        self.check_render(renderer_url, document_data['etalon'])

    def _data_file_name(self):
        return '/tmp/arlington/check_team_{}_round_{}.txt'.format(self.team_num, self.round_num)

    def _store_data(self, data):
        j_str = json.dumps(data)
        if not os.path.exists('/tmp/arlington'):
            os.makedirs('/tmp/arlington')
        with open(self._data_file_name(), 'w') as out:
            out.write(j_str)

    def _loads_data(self):
        with open(self._data_file_name()) as inp:
            return json.loads(inp.read())

    def run(self):
        # Check round before
        self.round_num -= 1
        if os.path.exists(self._data_file_name()):
            data = self._loads_data()
            for num, user in enumerate(data):
                self.check_user(user, num)

        self.reset_session()
        self.round_num += 1
        self.put_first()
        self.reset_session()
        self.put_second()
        self._store_data(self.users_data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Service Arlington checker')
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
    team_url = "http://" + arguments.team_ip + ":8888"
    checker = ArlingtonChecker(team_url, team_id, round_id, time_out)

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

    except Exception as e:
        status = "Down"
        status_message = str(e)
        # log error
        # TODO: (or not TODO) Log strange errors!
        # print(e)

    else:
        if status == "":
            status = "Up"

    print(json.dumps({'team_id': int(team_id), 'status_message': status_message, 'status': status}))
