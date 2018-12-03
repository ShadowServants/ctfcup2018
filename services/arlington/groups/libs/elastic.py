import requests
from django.conf import settings


class Collection(object):
    def __init__(self, collection):
        self.base = settings.ELASTIC_BASE
        self.collection = collection

    @property
    def _collection_url(self):
        return "{}{}/".format(self.base, self.collection)

    def create(self, _id, data):
        full_url = self._collection_url + "doc/" + str(_id)
        resp = requests.put(full_url, json=data)
        return Collection.check_created(resp)

    @staticmethod
    def _sort_field(field):
        if field.startswith('-'):
            return field.replace('-', '') + ":desc"
        else:
            return field + ":asc"

    def find(self, query, sort_by=None):
        full_url = self._collection_url + "_search?"
        if sort_by:
            full_url += "sort=" + self._sort_field(sort_by) + "&"
        full_url += "q=" + query
        resp = requests.get(full_url)
        if resp.status_code != 200:
            return [], False
        return resp.json().get('hits', {}).get('hits', []), True

    @staticmethod
    def check_created(response):
        try:
            if response.status_code in (200, 201) and response.json()['result'] in ('created', 'updated'):
                return True
            return False

        except Exception:
            return False


class SearchResult(object):
    def __init__(self, dictionary):
        self.id = dictionary.get('_id')
        for key, value in dictionary.get('_source').items():
            self.__setattr__(key, value)
