# -*- coding: utf-8 -*-


from . import __version__


USER_AGENT = 'Mergado-Api-Client-Python/version-{}'.format(__version__)

OAUTH_SERVER_HOST = 'https://app.mergado.com'

TOKEN_URI = OAUTH_SERVER_HOST + '/oauth2/token/'

MERGADO_API_URI = 'https://app.mergado.com/api/'
