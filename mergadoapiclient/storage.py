# -*- coding: utf-8 -*-


from datetime import datetime, timedelta


class BaseTokenStorage(object):
    """Token storage representation."""

    @classmethod
    def init(cls, token=None, expires_in=None):
        # dedicated init because if django ORM is used, overriding
        # __init__ may prevent the model instance from being saved.
        # see https://docs.djangoproject.com/en/1.8/ref/models/instances/
        self = cls()
        self.token = token
        self.expires_at = datetime.now() + timedelta(seconds=expires_in)
        return self

    @property
    def token_is_valid(self):
        return self.expires_at and self.expires_at > datetime.now()

    def save(self):
        """Stores storage instance. Default implementation does nothing."""

    def load(self):
        """Loads storage instance. Default implementation stores the
        token in memory and does nothing else.
        """
        if self.token and self.token_is_valid:
            return self
