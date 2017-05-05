# -*- coding: utf-8 -*-


import importlib
from datetime import datetime, timedelta
try:
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urljoin

from . import http, config


def _class_from_string(class_full_name):
    module_name, class_name = class_full_name.rsplit('.', 1)
    module = importlib.import_module(module_name)
    return getattr(module, class_name)


def build(credentials, api_version='0.3'):
    grant_type = credentials['grant_type']
    if grant_type == 'client_credentials':
        return ClientCredentialsClient(**credentials)
    else:
        NotImplementedError('Grant type not implemented.')


class BaseClient(object):

    def __init__(self, client_id, client_secret,
                 grant_type=None, storage_class=config.TOKEN_STORAGE_CLASS,
                 token_uri=config.TOKEN_URI, api_uri=config.MERGADO_API_URI):

        self.client_id = client_id
        self.client_secret = client_secret
        self.grant_type = grant_type

        self.TokenStorage = _class_from_string(storage_class)
        self.storage = self.TokenStorage()
        self.token_uri = token_uri
        self.api_uri = api_uri

    @property
    def _token_headers(self):
        token = self.fetch_token()
        return {'Authorization': 'Bearer {}'.format(token)}

    def _get_token_data(self):
        raise NotImplementedError()

    def fetch_token(self):
        self.storage = self.storage.load()
        if self.storage and self.storage.token_is_valid:
            return self.storage.token

        response = http.post(self.token_uri, json=self._get_token_data())
        response.raise_for_status()
        resp_data = response.json()

        self.storage = self.TokenStorage.init(
            token=resp_data['access_token'],
            expires_at=(datetime.now() +
                        timedelta(seconds=resp_data['expires_in'])),
        )
        self.storage.save()
        return self.storage.token

    def get_url(self, path):
        if path.startswith('/'):
            path = path[1:]
        return urljoin(self.api_uri, path)

    def request(self, method, path, **options):
        response = http.request(method, self.get_url(path),
                                headers=self._token_headers, **options)
        response.raise_for_status()
        return response.json()

    def get(self, path, **options):
        return self.request('GET', path, **options)

    def post(self, path, **options):
        return self.request('POST', path, **options)

    def patch(self, path, **options):
        return self.request('PATCH', path, **options)

    def delete(self, path, **options):
        return self.request('DELETE', path, **options)

    def iter(self, path, limit=100, offset=0, **options):
        while True:
            params = {'offset': offset, 'limit': limit}
            response = self.get(path, params=params, **options)
            data = response.get('data')

            if not data:
                break
            for item in data:
                yield item

            if len(data) < limit:
                break
            offset += limit


class ClientCredentialsClient(BaseClient):

    def _get_token_data(self):
        return {
            'grant_type': self.grant_type,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }
