# -*- coding: utf-8 -*-


from urlparse import urljoin
from datetime import datetime, timedelta

from . import http, config


def build(credentials, api_version='0.3'):
    grant_type = credentials['grant_type']
    if grant_type == 'client_credentials':
        return ClientCredentialsClient(**credentials)
    else:
        NotImplementedError('Grant type not implemented.')


class BaseClient(object):

    def __init__(self, client_id, client_secret, grant_type=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.grant_type = grant_type

        self.access_token = None
        self.token_expiry = None
        self.token_uri = config.TOKEN_URI
        self.token_entity_id = None

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
        return urljoin(config.MERGADO_API_URI, path)

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


class ClientCredentialsClient(BaseClient):

    def get_token_data(self):
        return {
            'grant_type': self.grant_type,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }
