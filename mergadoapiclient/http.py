# -*- coding: utf-8 -*-


"""
HTTP requests
=============

Extending all public API functions
from `Requests <http://docs.python-requests.org/>`_.
"""

from functools import wraps

import requests
from requests.exceptions import (RequestException, ConnectionError,
                                 HTTPError, URLRequired, TooManyRedirects)

from . import config


__all__ = ('get', 'options', 'head', 'post', 'put', 'patch', 'delete',
           'request',

           # Exceptions from requests.exceptions:
           'RequestException', 'ConnectionError', 'HTTPError', 'URLRequired',
           'TooManyRedirects')


def default_options(fn):
    """Decorator adding some default options for all HTTP requests.
    """
    default_headers = {
        'User-Agent': config.USER_AGENT,
        'Content-Type': 'application/json',
    }

    @wraps(fn)
    def wrapper(url, *args, **kwargs):
        additional_headers = kwargs.pop('headers', None) or {}
        headers = dict(default_headers, **additional_headers)
        return fn(url, headers=headers, *args, **kwargs)
    return wrapper


_decorators = [
    # from innermost to outermost
    default_options,
]


def _decorate(fn):
    for decorator in _decorators:
        fn = decorator(fn)
    return fn


get = _decorate(requests.get)
options = _decorate(requests.options)
head = _decorate(requests.head)
post = _decorate(requests.post)
put = _decorate(requests.put)
patch = _decorate(requests.patch)
delete = _decorate(requests.delete)
request = _decorate(requests.request)
