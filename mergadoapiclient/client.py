# -*- coding: utf-8 -*-


try:
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urljoin
from datetime import datetime, timedelta

from . import http, config


def build(credentials, api_version='0.3'):
    grant_type = credentials['grant_type']
    if grant_type == 'client_credentials':
        return ClientCredentialsClient(**credentials)
    else:
        NotImplementedError('Grant type not implemented.')


class BaseClient(object):

    def __init__(self, client_id, client_secret, grant_type=None,
                 token_uri=config.TOKEN_URI, api_uri=config.MERGADO_API_URI):

        self.client_id = client_id
        self.client_secret = client_secret
        self.grant_type = grant_type

        self.access_token = None
        self.token_expiry = None
        self.token_uri = token_uri
        self.token_entity_id = None
        self.api_uri = api_uri

    @property
    def token_is_valid(self):
        return self.token_expiry and self.token_expiry > datetime.now()

    @property
    def token_headers(self):
        if not self.token_is_valid:
            raise RuntimeError('Invalid token.')
        return {'Authorization': 'Bearer {}'.format(self.access_token)}

    def get_url(self, path):
        if path.startswith('/'):
            path = path[1:]
        return urljoin(self.api_uri, path)

    def get_token_data(self):
        raise NotImplementedError()

    def request_token(self):
        if self.token_is_valid:
            return self.access_token

        response = http.post(self.token_uri, json=self.get_token_data())
        response.raise_for_status()

        resp_data = response.json()
        self.access_token = resp_data['access_token']
        self.token_expiry = (datetime.now() +
                             timedelta(seconds=resp_data['expires_in']))
        self.token_entity_id = resp_data.get('entity_id')
        return self.access_token

    def request(self, method, path, **options):
        response = http.request(method, self.get_url(path),
                                headers=self.token_headers, **options)
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

    def get_token_data(self):
        return {
            'grant_type': self.grant_type,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }
